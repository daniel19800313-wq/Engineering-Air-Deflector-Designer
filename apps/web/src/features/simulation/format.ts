import type { EngineeringValue } from "../../api/contracts";

export function formatValue(item: EngineeringValue, digits = 3): string {
  if (item.availability === "unavailable" || item.value === null) return "Unavailable";
  return `${item.value.toFixed(digits)} ${item.unit ?? ""}`.trim();
}
