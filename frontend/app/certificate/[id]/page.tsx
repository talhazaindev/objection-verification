import { getCertificate } from "@/lib/api";
import { notFound } from "next/navigation";
import { Shield } from "lucide-react";
import CertificateCard from "@/components/CertificateCard";

export default async function CertificatePage({
  params,
}: {
  params: { id: string };
}) {
  let data;
  try {
    data = await getCertificate(params.id);
  } catch {
    notFound();
  }

  const { certificate, attribution } = data;

  return (
    <main className="min-h-screen px-6 py-20">
      <div className="mx-auto max-w-2xl">
        <div className="text-center mb-8">
          <Shield className="mx-auto h-12 w-12 text-emerald-400 mb-4" />
          <h1 className="text-3xl font-bold">Verification Certificate</h1>
          <p className="text-slate-400 mt-2">
            This certificate confirms independent evidence verification without
            revealing source identity.
          </p>
        </div>

        <CertificateCard
          certificate={certificate}
          attributionLongForm={attribution.long_form}
          attributionLegalDisclaimer={attribution.legal_disclaimer}
          showAttributionDisclaimer
        />
      </div>
    </main>
  );
}
