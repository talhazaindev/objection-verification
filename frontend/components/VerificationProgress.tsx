"use client";

import { Loader2, Hash, Brain, FileSearch, BadgeCheck } from "lucide-react";

const STEPS = [
  { icon: Hash, label: "Verifying client capture hashes" },
  { icon: FileSearch, label: "Metadata forensics & anomaly scan" },
  { icon: Brain, label: "Presidio PII redaction + AI analysis" },
  { icon: BadgeCheck, label: "Generating certificate" },
];

export default function VerificationProgress() {
  return (
    <div className="card-glass p-6 border-emerald-500/20">
      <div className="flex items-center gap-3 mb-6">
        <Loader2 className="h-5 w-5 animate-spin text-emerald-400" />
        <p className="font-medium">Analyzing evidence package...</p>
      </div>
      <div className="space-y-4">
        {STEPS.map((step, i) => (
          <div key={i} className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-500/10">
              <step.icon className="h-4 w-4 text-emerald-400" />
            </div>
            <span className="text-sm text-slate-400">{step.label}</span>
            <div className="ml-auto h-1.5 flex-1 max-w-[120px] rounded-full bg-slate-800 overflow-hidden">
              <div
                className="h-full bg-emerald-500/60 rounded-full animate-pulse"
                style={{ width: `${((i + 1) / STEPS.length) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
