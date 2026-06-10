"use client";

import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, File, X, Hash } from "lucide-react";
import { buildProvenanceRecord, type ClientProvenance } from "@/lib/hash";

export interface CapturedFile {
  file: File;
  provenance: ClientProvenance;
}

interface UploadZoneProps {
  captures: CapturedFile[];
  onCapturesChange: (captures: CapturedFile[]) => void;
  disabled?: boolean;
}

export default function UploadZone({
  captures,
  onCapturesChange,
  disabled = false,
}: UploadZoneProps) {
  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const newCaptures = await Promise.all(
        acceptedFiles.map(async (file) => ({
          file,
          provenance: await buildProvenanceRecord(file),
        }))
      );
      onCapturesChange([...captures, ...newCaptures]);
    },
    [captures, onCapturesChange]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    disabled,
    accept: {
      "text/*": [".txt", ".md"],
      "application/pdf": [".pdf"],
      "audio/*": [".mp3", ".wav"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"],
    },
  });

  const removeFile = (index: number) => {
    onCapturesChange(captures.filter((_, i) => i !== index));
  };

  return (
    <div>
      <div
        {...getRootProps()}
        className={`cursor-pointer rounded-2xl border-2 border-dashed p-12 text-center transition ${
          disabled ? "opacity-50 cursor-not-allowed" : ""
        } ${
          isDragActive
            ? "border-emerald-500 bg-emerald-500/5"
            : "border-slate-700 bg-slate-900/50 hover:border-slate-600"
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-10 w-10 text-slate-500 mb-4" />
        <p className="text-lg font-medium">
          {isDragActive ? "Drop files here" : "Drag & drop evidence files"}
        </p>
        <p className="text-sm text-slate-500 mt-1">
          SHA-256 hashed at capture · Supports .txt, .pdf, .mp3, .wav, .docx
        </p>
      </div>

      {captures.length > 0 && (
        <div className="mt-6 space-y-2">
          {captures.map((capture, i) => (
            <div
              key={`${capture.file.name}-${i}`}
              className="rounded-xl bg-slate-800/50 px-4 py-3"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <File className="h-5 w-5 text-emerald-400" />
                  <span className="text-sm">{capture.file.name}</span>
                  <span className="text-xs text-slate-500">
                    {(capture.file.size / 1024).toFixed(1)} KB
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => removeFile(i)}
                  disabled={disabled}
                  className="rounded-lg p-1 hover:bg-slate-700 text-slate-500 disabled:opacity-50"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
              <div className="mt-2 flex items-center gap-2 text-xs text-slate-500">
                <Hash className="h-3 w-3 text-emerald-500/70" />
                <span className="font-mono truncate">
                  {capture.provenance.client_hash.slice(0, 20)}...
                </span>
                <span className="text-emerald-500/80">captured at intake</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
