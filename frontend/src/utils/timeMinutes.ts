export function minutesToTimeInput(totalMinutes: number): string {
  let h = Math.floor(totalMinutes / 60) % 24;
  let m = totalMinutes % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

export function timeInputToMinutes(value: string): number {
  let parts = value.split(":");
  let h = parseInt(parts[0] || "0", 10);
  let m = parseInt(parts[1] || "0", 10);
  return h * 60 + m;
}

export const WEEKDAY_LABELS = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday"
];
