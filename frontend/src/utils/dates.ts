/** Date parsing and display helpers for the UI. */

export function isoToDateInput(iso: string | null | undefined): string {
  if (!iso) {
    return "";
  }
  return iso.slice(0, 10);
}

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

function pad2(n: number): string {
  return String(n).padStart(2, "0");
}

/** Value for `<input type="datetime-local" />` in local time. */
export function toDatetimeLocalValue(iso: string): string {
  const d = new Date(iso);
  return `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}T${pad2(d.getHours())}:${pad2(d.getMinutes())}`;
}

/** Parse datetime-local string to ISO (UTC) for the API. */
export function fromDatetimeLocalToIso(value: string): string {
  const d = new Date(value);
  return d.toISOString();
}

export function triggerBlobDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.rel = "noopener";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
