/** Building the fixed three-week calendar grid from week boundaries. */

export function getStartOfCurrentWeek(): Date {
  const now = new Date();
  const start = new Date(now);
  start.setHours(0, 0, 0, 0);
  const dayIndex = start.getDay();
  start.setDate(start.getDate() - dayIndex);
  return start;
}

export function getDateKey(value: Date): string {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export function getThreeWeekDays(weekStart: Date): Date[] {
  const days: Date[] = [];
  for (let offset = 0; offset < 21; offset++) {
    const day = new Date(weekStart);
    day.setDate(weekStart.getDate() + offset);
    days.push(day);
  }
  return days;
}
