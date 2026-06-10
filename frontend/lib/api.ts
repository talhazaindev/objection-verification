import type {
  CertificatePublicResponse,
  VerificationResponse,
} from "./types";

function getApiBase(): string {
  // Server-side (SSR): talk to backend directly inside the container
  if (typeof window === "undefined") {
    return (
      process.env.INTERNAL_API_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      "http://localhost:8000"
    );
  }
  // Browser: same-origin via nginx when NEXT_PUBLIC_API_URL is unset
  return process.env.NEXT_PUBLIC_API_URL || "";
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
  files: File[]
): Promise<VerificationResponse> {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));

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
