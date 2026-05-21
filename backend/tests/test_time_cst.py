from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.core.timeutil import PAST_TIME_MESSAGE, asCstNaive, assertNotInPast, nowCst


def test_now_cst_is_naive():
    n = nowCst()
    assert n.tzinfo is None


def test_as_cst_naive_converts_aware():
    utc = datetime(2026, 8, 19, 18, 0, 0, tzinfo=ZoneInfo("UTC"))
    local = asCstNaive(utc)
    assert local.tzinfo is None
    # CDT is UTC-5 in August
    assert local.hour == 13


def test_assert_not_in_past_rejects_yesterday():
    past = nowCst() - timedelta(hours=2)
    try:
        assertNotInPast(past)
        assert False, "expected ValueError"
    except ValueError as exc:
        assert str(exc) == PAST_TIME_MESSAGE


def test_assert_not_in_past_allows_future():
    future = nowCst() + timedelta(hours=2)
    assertNotInPast(future)


def test_create_block_in_past_rejected(client):
    for day in range(5):
        client.post(
            "/api/availability",
            json={"day_of_week": day, "start_minutes": 0, "end_minutes": 1440}
        )
    past_start = (nowCst() - timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
    past_end = past_start + timedelta(hours=1)
    response = client.post(
        "/api/schedule/blocks",
        json={
            "title": "Too late",
            "start_time": past_start.isoformat(),
            "end_time": past_end.isoformat()
        }
    )
    assert response.status_code == 422
    assert "already passed" in response.json()["detail"].lower()
