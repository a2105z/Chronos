export function getDateKey(value: Date): string {
  let year = value.getFullYear();
  let month = String(value.getMonth() + 1).padStart(2, "0");
  let day = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

/** Start of the ISO week (Monday) containing `reference`, at local midnight. */
export function getStartOfWeekMonday(reference: Date = new Date()): Date {
  let d = new Date(reference);
  d.setHours(0, 0, 0, 0);
  let day = d.getDay();
  let diffToMonday = 1 - day;
  if (day === 0) {
    diffToMonday = -6;
  }
  d.setDate(d.getDate() + diffToMonday);
  return d;
}

export function addDays(date: Date, days: number): Date {
  let next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

export function addWeeks(monday: Date, weeks: number): Date {
  return addDays(monday, weeks * 7);
}

/** `count` consecutive days starting at `weekMonday` (inclusive). */
export function getWeekDaysFromMonday(weekMonday: Date, count: number): Date[] {
  let days: Date[] = [];
  for (let i = 0; i < count; i++) {
    days.push(addDays(weekMonday, i));
  }
  return days;
}
