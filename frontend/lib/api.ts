import type { ClientProvenance } from "./hash";
import type {
  CertificatePublicResponse,
  VerificationResponse,
} from "./types";

function isLocalDevApiUrl(url: string): boolean {
  return /localhost|127\.0\.0\.1/i.test(url);
}

function getApiBase(): string {
  // Server-side (SSR): talk to backend directly inside the unified container
  if (typeof window === "undefined") {
    return (
      process.env.INTERNAL_API_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      "http://localhost:8000"
    );
  }

  const configured = process.env.NEXT_PUBLIC_API_URL?.trim();
  // Ignore localhost URLs in the browser — they only work for split local dev,
  // not Railway/Docker where nginx serves API on the same origin.
  if (configured && !isLocalDevApiUrl(configured)) {
    return configured.replace(/\/$/, "");
  }
  return "";
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = response.statusText;
    try {
      const error = await response.json();
      if (error && typeof error.detail === "string") {
        message = error.detail;
      }
    } catch {
      // use statusText if body is not JSON
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export async function verifyEvidence(
  files: File[],
  provenance: ClientProvenance[] = []
): Promise<VerificationResponse> {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  formData.append("provenance", JSON.stringify(provenance));

  const response = await fetch(`${getApiBase()}/api/verify/`, {
    method: "POST",
    body: formData,
  });

  return handleResponse<VerificationResponse>(response);
}

export async function getCertificate(
  certificateId: string
): Promise<CertificatePublicResponse> {
  const response = await fetch(
    `${getApiBase()}/api/verify/certificate/${certificateId}`
  );
  return handleResponse<CertificatePublicResponse>(response);
}
