"use client";

import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, File, X } from "lucide-react";

interface UploadZoneProps {
  files: File[];
  onFilesChange: (files: File[]) => void;
  disabled?: boolean;
}

export default function UploadZone({
  files,
  onFilesChange,
  disabled = false,
}: UploadZoneProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      onFilesChange([...files, ...acceptedFiles]);
    },
    [files, onFilesChange]
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
    onFilesChange(files.filter((_, i) => i !== index));
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
          Supports .txt, .pdf, .mp3, .wav, .docx
        </p>
      </div>

      {files.length > 0 && (
        <div className="mt-6 space-y-2">
          {files.map((file, i) => (
            <div
              key={`${file.name}-${i}`}
              className="flex items-center justify-between rounded-xl bg-slate-800/50 px-4 py-3"
            >
              <div className="flex items-center gap-3">
                <File className="h-5 w-5 text-emerald-400" />
                <span className="text-sm">{file.name}</span>
                <span className="text-xs text-slate-500">
                  {(file.size / 1024).toFixed(1)} KB
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
          ))}
        </div>
      )}
    </div>
  );
}
