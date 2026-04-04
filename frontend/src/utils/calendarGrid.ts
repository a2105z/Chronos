/** Week boundaries aligned with backend `day_of_week` (0 = Monday). */

export function getDateKey(value: Date): string {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

/** Start of the ISO week (Monday) containing `reference`, at local midnight. */
export function getStartOfWeekMonday(reference: Date = new Date()): Date {
  const d = new Date(reference);
  d.setHours(0, 0, 0, 0);
  const day = d.getDay();
  const diffToMonday = day === 0 ? -6 : 1 - day;
  d.setDate(d.getDate() + diffToMonday);
  return d;
}

export function addDays(date: Date, days: number): Date {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

export function addWeeks(monday: Date, weeks: number): Date {
  return addDays(monday, weeks * 7);
}

/** `count` consecutive days starting at `weekMonday` (inclusive). */
export function getWeekDaysFromMonday(weekMonday: Date, count: number): Date[] {
  const days: Date[] = [];
  for (let i = 0; i < count; i++) {
    days.push(addDays(weekMonday, i));
  }
  return days;
}
