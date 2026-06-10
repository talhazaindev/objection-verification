"use client";

import { useState } from "react";
import { Hash, Clock, BarChart3, Shield } from "lucide-react";
import type { Certificate, ReliabilityTier } from "@/lib/types";
import AttributionBlock from "./AttributionBlock";

interface CertificateCardProps {
  certificate: Certificate;
  attributionLongForm: string;
  attributionLegalDisclaimer?: string;
  corroboratedCount?: number;
  showAttributionDisclaimer?: boolean;
}

function tierBadgeClass(tier: ReliabilityTier): string {
  switch (tier) {
    case "high":
      return "bg-emerald-500/20 text-emerald-400";
    case "medium":
      return "bg-yellow-500/20 text-yellow-400";
    default:
      return "bg-red-500/20 text-red-400";
  }
}

export default function CertificateCard({
  certificate,
  attributionLongForm,
  attributionLegalDisclaimer,
  corroboratedCount,
  showAttributionDisclaimer = false,
}: CertificateCardProps) {
  const [copied, setCopied] = useState(false);

  const copyAttribution = () => {
    navigator.clipboard.writeText(attributionLongForm);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="card-glass p-6 border-emerald-500/20">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-sm text-slate-500">Certificate ID</p>
          <p className="font-mono text-lg">{certificate.certificate_id}</p>
        </div>
        <span
          className={`rounded-full px-3 py-1 text-sm font-medium ${tierBadgeClass(certificate.reliability_tier)}`}
        >
          {certificate.reliability_tier.toUpperCase()} CONFIDENCE
        </span>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="rounded-lg bg-slate-800/50 p-3">
          <BarChart3 className="h-4 w-4 text-slate-400 mb-1" />
          <p className="text-xs text-slate-500">Confidence</p>
          <p className="text-xl font-bold text-emerald-400">
            {(certificate.overall_confidence * 100).toFixed(1)}%
          </p>
        </div>
        <div className="rounded-lg bg-slate-800/50 p-3">
          <Shield className="h-4 w-4 text-slate-400 mb-1" />
          <p className="text-xs text-slate-500">Files</p>
          <p className="text-xl font-bold">{certificate.evidence_count}</p>
        </div>
        <div className="rounded-lg bg-slate-800/50 p-3">
          <Clock className="h-4 w-4 text-slate-400 mb-1" />
          <p className="text-xs text-slate-500">
            {corroboratedCount !== undefined ? "Corroborated" : "Issued"}
          </p>
          <p className="text-xl font-bold">
            {corroboratedCount !== undefined
              ? corroboratedCount
              : new Date(certificate.timestamp).toLocaleDateString()}
          </p>
        </div>
      </div>

      <p className="text-sm text-slate-400 mb-4">
        {certificate.verification_summary}
      </p>

      <div className="rounded-xl bg-slate-800/50 p-4 mb-4">
        <p className="text-xs text-slate-500 mb-3">Verified Evidence</p>
        <div className="space-y-2">
          {certificate.evidence_breakdown.map((item, i) => (
            <div
              key={i}
              className="flex items-center justify-between text-sm"
            >
              <span className="text-slate-300 capitalize">
                {item.evidence_type.replace(/_/g, " ")}
              </span>
              <div className="flex items-center gap-3">
                <span className="font-mono text-xs text-slate-500">
                  {item.content_hash.slice(0, 16)}...
                </span>
                <span className="text-xs text-slate-500">
                  {item.file_size_kb} KB
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <AttributionBlock
        longForm={attributionLongForm}
        legalDisclaimer={attributionLegalDisclaimer}
        showDisclaimer={showAttributionDisclaimer}
        copied={copied}
        onCopy={copyAttribution}
      />

      <div className="mt-4 flex items-center gap-2 text-xs text-slate-600">
        <Hash className="h-3 w-3" />
        <span className="font-mono">{certificate.hash_chain}</span>
      </div>
    </div>
  );
}
