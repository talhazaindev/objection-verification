import { Shield, Hash, Clock, BarChart3, FileText } from "lucide-react";

export default function ExampleCertificate() {
  return (
    <div className="card-glass p-8 border-emerald-500/20">
      <div className="flex items-center gap-3 mb-6">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/10">
          <Shield className="h-6 w-6 text-emerald-400" />
        </div>
        <div>
          <h3 className="text-lg font-semibold">
            Objection Verification Certificate
          </h3>
          <p className="text-sm text-slate-400">OBJ-A7B3C9D8E1F2</p>
        </div>
        <div className="ml-auto">
          <span className="rounded-full bg-emerald-500/20 px-3 py-1 text-sm font-medium text-emerald-400">
            HIGH CONFIDENCE
          </span>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3 mb-6">
        <div className="rounded-xl bg-slate-800/50 p-4">
          <Clock className="h-5 w-5 text-slate-400 mb-2" />
          <p className="text-xs text-slate-500">Timestamp</p>
          <p className="text-sm font-mono">2026-06-09T13:01:00Z</p>
        </div>
        <div className="rounded-xl bg-slate-800/50 p-4">
          <BarChart3 className="h-5 w-5 text-slate-400 mb-2" />
          <p className="text-xs text-slate-500">Confidence Score</p>
          <p className="text-2xl font-bold text-emerald-400">87.3%</p>
        </div>
        <div className="rounded-xl bg-slate-800/50 p-4">
          <FileText className="h-5 w-5 text-slate-400 mb-2" />
          <p className="text-xs text-slate-500">Evidence Files</p>
          <p className="text-2xl font-bold">5</p>
        </div>
      </div>

      <div className="rounded-xl bg-slate-800/50 p-4 mb-4">
        <p className="text-xs text-slate-500 mb-2">Evidence Breakdown</p>
        <div className="space-y-2">
          {[
            { type: "Intake Notes", hash: "a3f7...9e2d", size: "12 KB" },
            { type: "Email Chain", hash: "b8c1...4a7f", size: "45 KB" },
            { type: "Audio Recording", hash: "d2e5...1b8c", size: "2.1 MB" },
            { type: "Data Memo", hash: "f9a3...7d4e", size: "8 KB" },
            { type: "Personal Notes", hash: "c4b8...2f1a", size: "6 KB" },
          ].map((item, i) => (
            <div key={i} className="flex items-center justify-between text-sm">
              <span className="text-slate-300">{item.type}</span>
              <div className="flex items-center gap-4 text-slate-500">
                <span className="font-mono text-xs">{item.hash}</span>
                <span>{item.size}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-xl bg-slate-800/50 p-4">
        <p className="text-xs text-slate-500 mb-2">Attribution Language</p>
        <p className="text-sm text-slate-300 italic">
          &ldquo;a source whose claims have been independently verified with high
          confidence through Objection&apos;s independent evidence verification
          system (Certificate ID: OBJ-A7B3C9D8E1F2, Confidence: 87%)&rdquo;
        </p>
      </div>

      <div className="mt-4 flex items-center gap-2 text-xs text-slate-500">
        <Hash className="h-3 w-3" />
        <span className="font-mono">Hash Chain: e7f3a9...2d8b1c</span>
      </div>
    </div>
  );
}
