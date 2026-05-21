"""Unit tests for contiguous block coalescing in the allocator."""

from datetime import datetime

from app.models.task import Task
from app.services.scheduler.allocator import (
    AllocatedBlock,
    allocateTasks,
    coalesceContiguousBlocks,
)


def test_coalesceContiguousBlocks_merges_adjacent_same_task():
    """Adjacent same-task fragments merge into one block."""
    b1 = AllocatedBlock(1, "t", datetime(2030, 1, 7, 9, 0), datetime(2030, 1, 7, 9, 15), 15)
    b2 = AllocatedBlock(1, "t", datetime(2030, 1, 7, 9, 15), datetime(2030, 1, 7, 9, 30), 15)
    out = coalesceContiguousBlocks([b1, b2], None)
    assert len(out) == 1
    assert out[0].duration_minutes == 30
    assert out[0].start_time == datetime(2030, 1, 7, 9, 0)
    assert out[0].end_time == datetime(2030, 1, 7, 9, 30)


def test_coalesceContiguousBlocks_respects_max_continuous():
    """Does not merge when combined duration would exceed max continuous work."""
    b1 = AllocatedBlock(1, "t", datetime(2030, 1, 7, 9, 0), datetime(2030, 1, 7, 9, 15), 15)
    b2 = AllocatedBlock(1, "t", datetime(2030, 1, 7, 9, 15), datetime(2030, 1, 7, 9, 30), 15)
    out = coalesceContiguousBlocks([b1, b2], 15)
    assert len(out) == 2


def test_allocateTasks_returns_coalesced_blocks():
    """allocateTasks merges contiguous same-task slot chunks after allocation."""
    task = Task(
        id=1,
        name="Study",
        estimated_duration_minutes=30,
        priority=1,
        splittable=True,
    )
    slots = [
        (datetime(2030, 1, 7, 9, 0), datetime(2030, 1, 7, 9, 15)),
        (datetime(2030, 1, 7, 9, 15), datetime(2030, 1, 7, 9, 30)),
    ]
    result = allocateTasks([task], slots, constraints=None)
    assert result.unscheduled == []
    assert len(result.blocks) == 1
    assert result.blocks[0].task_id == 1
    assert result.blocks[0].duration_minutes == 30
    assert result.blocks[0].start_time == datetime(2030, 1, 7, 9, 0)
    assert result.blocks[0].end_time == datetime(2030, 1, 7, 9, 30)
