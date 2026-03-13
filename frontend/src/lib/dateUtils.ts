/**
 * Parse a UTC timestamp string from the backend.
 * Backend stores naive UTC datetimes and Pydantic serializes without "Z" suffix.
 * JavaScript new Date() treats strings without timezone as local time, so we append "Z".
 */
export function parseUTCTimestamp(iso: string): Date {
  if (!iso.endsWith("Z") && !iso.includes("+") && !iso.includes("-", 10)) {
    return new Date(iso + "Z");
  }
  return new Date(iso);
}
