export const COLORS = {
  ink: "26,26,26",
  muted: "90,98,106",
  blue: "45,102,133",
  red: "164,62,70",
  green: "62,120,87",
  gold: "169,120,47",
};

export function statusColor(status) {
  switch (status) {
    case "refuted": return COLORS.red;
    case "resolved": return COLORS.green;
    case "highlight": return COLORS.gold;
    case "scientific": return COLORS.blue;
    case "neutral": return COLORS.muted;
    default: return COLORS.ink;
  }
}
