"use client";

import { Copy, Check } from "lucide-react";

interface AttributionBlockProps {
  longForm: string;
  legalDisclaimer?: string;
  showDisclaimer?: boolean;
  copied: boolean;
  onCopy: () => void;
}

export default function AttributionBlock({
  longForm,
  legalDisclaimer,
  showDisclaimer = false,
  copied,
  onCopy,
}: AttributionBlockProps) {
  return (
    <div className="rounded-lg bg-slate-800/50 p-4">
      <div className="flex items-center justify-between mb-2">
        <p className="text-xs text-slate-500">Attribution Language</p>
        <button
          type="button"
          onClick={onCopy}
          className="flex items-center gap-1 text-xs text-emerald-400 hover:text-emerald-300"
        >
          {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
          {copied ? "Copied!" : "Copy"}
        </button>
      </div>
      <p className="text-sm text-slate-300 italic">&ldquo;{longForm}&rdquo;</p>
      {showDisclaimer && legalDisclaimer && (
        <p className="text-xs text-slate-500 mt-3">{legalDisclaimer}</p>
      )}
    </div>
  );
}
