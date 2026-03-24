"""Export scheduled blocks to .ics format for calendar apps."""

from icalendar import Calendar, Event

from app.schemas.schedule import ScheduledBlockRead


class ExportService:
    """Build .ics calendar files from scheduled blocks."""

    @staticmethod
    def toIcs(blocks: list[ScheduledBlockRead]) -> bytes:
        """Convert blocks to .ics format (RFC 5545)."""
        cal = Calendar()
        cal.add("prodid", "-//Chronos//Scheduling Engine//EN")
        cal.add("version", "2.0")

        for block in blocks:
            event = Event()
            event.add("summary", block.task_name)
            event.add("dtstart", block.start_time)
            event.add("dtend", block.end_time)
            event.add("description", f"Task ID: {block.task_id}")
            cal.add_component(event)

        icalBytes = cal.to_ical()
        return icalBytes
