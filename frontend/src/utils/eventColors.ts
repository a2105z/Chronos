const PALETTE = [
  { key: "teal", label: "Tasks", bg: "#0d9488", border: "#0f766e", text: "#fff", soft: false },
  { key: "blue", label: "Focus", bg: "#3b82f6", border: "#2563eb", text: "#fff", soft: false },
  { key: "orange", label: "Deep work", bg: "#f97316", border: "#ea580c", text: "#fff", soft: false },
  { key: "rose", label: "Personal", bg: "#fb7185", border: "#e11d48", text: "#fff", soft: false },
  { key: "violet", label: "Study", bg: "#8b5cf6", border: "#7c3aed", text: "#fff", soft: false },
  { key: "lime", label: "Other", bg: "#65a30d", border: "#4d7c0f", text: "#fff", soft: false }
];

export function colorForTitle(title: string) {
  const lower = title.toLowerCase();
  if (lower.includes("lunch") || lower.includes("break") || lower.includes("personal")) {
    return { ...PALETTE[3], soft: true, bg: "#fff", text: "#e11d48", border: "#fb7185" };
  }
  if (lower.includes("study") || lower.includes("exam") || lower.includes("stat")) {
    return PALETTE[4];
  }
  if (lower.includes("meeting") || lower.includes("call")) {
    return PALETTE[1];
  }
  if (lower.includes("deep") || lower.includes("resume") || lower.includes("write")) {
    return PALETTE[2];
  }
  let hash = 0;
  for (let i = 0; i < title.length; i++) {
    hash = (hash + title.charCodeAt(i) * (i + 1)) % 997;
  }
  return PALETTE[hash % PALETTE.length];
}
