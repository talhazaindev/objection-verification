"use client";

import { useState } from "react";
import Link from "next/link";
import { Loader2, Shield } from "lucide-react";
import UploadZone from "@/components/UploadZone";
import VerificationProgress from "@/components/VerificationProgress";
import CertificateCard from "@/components/CertificateCard";
import { verifyEvidence } from "@/lib/api";
import type { VerificationResponse } from "@/lib/types";

export default function VerifyPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [verifying, setVerifying] = useState(false);
  const [result, setResult] = useState<VerificationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleVerify = async () => {
    if (files.length === 0) {
      setError("Please upload at least one evidence file.");
      return;
    }
    setVerifying(true);
    setError(null);
    setResult(null);
    try {
      const data = await verifyEvidence(files);
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Verification failed. Please try again."
      );
    } finally {
      setVerifying(false);
    }
  };

  return (
    <main className="min-h-screen px-6 py-20">
      <div className="mx-auto max-w-3xl">
        <h1 className="text-3xl font-bold mb-2">Verify Evidence Package</h1>
        <p className="text-slate-400 mb-8">
          Upload your evidence files. We&apos;ll verify integrity, analyze
          consistency, and generate a privacy-preserving certificate.
        </p>

        <UploadZone
          files={files}
          onFilesChange={setFiles}
          disabled={verifying}
        />

        <button
          type="button"
          onClick={handleVerify}
          disabled={verifying || files.length === 0}
          className="mt-6 w-full rounded-xl bg-emerald-500 py-4 font-semibold text-slate-950 hover:bg-emerald-400 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center gap-2"
        >
          {verifying ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" />
              Analyzing Evidence...
            </>
          ) : (
            <>
              <Shield className="h-5 w-5" />
              Verify Evidence Package
            </>
          )}
        </button>

        {verifying && (
          <div className="mt-6">
            <VerificationProgress />
          </div>
        )}

        {error && (
          <div className="mt-4 rounded-xl bg-red-500/10 border border-red-500/20 p-4 text-red-400 text-sm">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-10 space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Verification Complete</h2>
              <Link
                href={`/certificate/${result.certificate.certificate_id}`}
                className="text-sm text-emerald-400 hover:text-emerald-300"
              >
                View public certificate →
              </Link>
            </div>

            <CertificateCard
              certificate={result.certificate}
              attributionLongForm={result.attribution.long_form}
              corroboratedCount={
                result.analysis.corroboration_results.length
              }
            />

            <div className="card-glass p-6">
              <h3 className="font-semibold mb-4">Analysis Details</h3>

              {result.analysis.key_findings.length > 0 && (
                <div className="mb-4">
                  <p className="text-xs text-emerald-400 mb-2">Key Findings</p>
                  <ul className="space-y-1">
                    {result.analysis.key_findings.map((finding, i) => (
                      <li
                        key={i}
                        className="text-sm text-slate-300 flex items-start gap-2"
                      >
                        <span className="text-emerald-400 mt-1">•</span>
                        {finding}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {result.analysis.red_flags.length > 0 && (
                <div>
                  <p className="text-xs text-red-400 mb-2">Red Flags</p>
                  <ul className="space-y-1">
                    {result.analysis.red_flags.map((flag, i) => (
                      <li
                        key={i}
                        className="text-sm text-slate-300 flex items-start gap-2"
                      >
                        <span className="text-red-400 mt-1">•</span>
                        {flag}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
