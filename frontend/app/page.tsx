import Link from "next/link";
import {
  Shield,
  Lock,
  FileCheck,
  BadgeCheck,
  ArrowRight,
} from "lucide-react";
import ExampleCertificate from "@/components/ExampleCertificate";

export default function MarketingPage() {
  return (
    <main className="min-h-screen">
      <section className="relative overflow-hidden px-6 pt-20 pb-32">
        <div className="mx-auto max-w-5xl text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-4 py-1.5 text-sm text-emerald-400">
            <Shield className="h-4 w-4" />
            <span>Privacy-Preserving Source Verification</span>
          </div>
          <h1 className="text-5xl font-bold tracking-tight sm:text-7xl">
            Prove the evidence.
            <br />
            <span className="gradient-text">Protect the source.</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-400">
            Objection verifies evidence from anonymous sources and generates
            public, privacy-preserving certificates with ready-to-use
            attribution language. Anyone can hash a file after creating it —
            we solve for <em>before</em>.
          </p>
          <div className="mt-10 flex justify-center gap-4">
            <Link
              href="/verify"
              className="inline-flex items-center gap-2 rounded-xl bg-emerald-500 px-6 py-3 font-semibold text-slate-950 hover:bg-emerald-400 transition"
            >
              Verify Evidence <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      <section className="border-t border-slate-800 px-6 py-24">
        <div className="mx-auto max-w-5xl">
          <h2 className="text-3xl font-bold text-center mb-16">How It Works</h2>
          <div className="grid gap-8 md:grid-cols-3">
            {[
              {
                icon: Lock,
                title: "Secure Intake",
                desc: "Evidence is hashed on upload. SHA-256 fingerprints ensure tamper detection from moment zero.",
              },
              {
                icon: FileCheck,
                title: "AI-Powered Analysis",
                desc: "Multiple evidence types are cross-referenced for consistency, corroboration, and plausibility by specialized AI agents.",
              },
              {
                icon: BadgeCheck,
                title: "Public Certificate",
                desc: "A privacy-preserving certificate is generated with a confidence score and publication-ready attribution language.",
              },
            ].map((step, i) => (
              <div key={i} className="card-glass p-8">
                <step.icon className="h-10 w-10 text-emerald-400 mb-4" />
                <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                <p className="text-slate-400">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="border-t border-slate-800 px-6 py-24">
        <div className="mx-auto max-w-3xl">
          <h2 className="text-3xl font-bold text-center mb-4">
            Example Certificate
          </h2>
          <p className="text-center text-slate-400 mb-12">
            What journalists and readers see — zero source identity, maximum
            transparency.
          </p>
          <ExampleCertificate />
        </div>
      </section>

      <section className="border-t border-slate-800 px-6 py-24 text-center">
        <h2 className="text-3xl font-bold mb-4">Ready to verify?</h2>
        <p className="text-slate-400 mb-8">
          Upload your evidence package and receive a certificate in minutes.
        </p>
        <Link
          href="/verify"
          className="inline-flex items-center gap-2 rounded-xl bg-emerald-500 px-8 py-4 font-semibold text-slate-950 hover:bg-emerald-400 transition"
        >
          Start Verification <ArrowRight className="h-4 w-4" />
        </Link>
      </section>
    </main>
  );
}
