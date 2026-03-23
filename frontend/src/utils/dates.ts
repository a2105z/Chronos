/** Date parsing and display helpers for the UI. */

export function toIsoDateFromInput(value: string): string | null {
  if (value === "") {
    return null;
  }
  const parsed = new Date(value);
  return parsed.toISOString();
}

export function toIsoDateTime(date: Date): string {
  return date.toISOString();
}

export function formatTimeFromIso(value: string): string {
  const date = new Date(value);
  return date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}
