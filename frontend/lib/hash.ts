export interface ClientProvenance {
  filename: string;
  client_hash: string;
  captured_at: string;
}

export async function computeClientHash(file: File): Promise<string> {
  const buffer = await file.arrayBuffer();
  const hashBuffer = await crypto.subtle.digest("SHA-256", buffer);
  return Array.from(new Uint8Array(hashBuffer))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

export async function buildProvenanceRecord(
  file: File
): Promise<ClientProvenance> {
  const client_hash = await computeClientHash(file);
  return {
    filename: file.name,
    client_hash,
    captured_at: new Date().toISOString(),
  };
}
