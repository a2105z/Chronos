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
  let parsed = new Date(value);
  return parsed.toISOString();
}

export function toIsoDateTime(date: Date): string {
  return toLocalApiDateTime(date);
}

/** Local wall-clock datetime for the API (no UTC shift). */
export function toLocalApiDateTime(date: Date): string {
  return `${date.getFullYear()}-${pad2(date.getMonth() + 1)}-${pad2(date.getDate())}T${pad2(date.getHours())}:${pad2(date.getMinutes())}:${pad2(date.getSeconds())}`;
}

export function formatTimeFromIso(value: string): string {
  let date = new Date(value);
  return date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}

function pad2(n: number): string {
  return String(n).padStart(2, "0");
}

/** Value for `<input type="datetime-local" />` in local time. */
export function toDatetimeLocalValue(iso: string): string {
  let d = new Date(iso);
  return `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}T${pad2(d.getHours())}:${pad2(d.getMinutes())}`;
}

/** Parse datetime-local string to local API datetime (no UTC shift). */
export function fromDatetimeLocalToIso(value: string): string {
  // value is already "YYYY-MM-DDTHH:mm" in local time
  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(value)) {
    return `${value}:00`;
  }
  return toLocalApiDateTime(new Date(value));
}

export function triggerBlobDownload(blob: Blob, filename: string): void {
  let url = URL.createObjectURL(blob);
  let a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.rel = "noopener";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
