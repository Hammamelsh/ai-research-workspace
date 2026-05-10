"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { uploadDocument, embedDocument } from "@/lib/api";
import toast from "react-hot-toast";
import { FileText, Upload, CheckCircle, Loader } from "lucide-react";

interface Props {
  onDocumentReady: (fileId: string, filename: string) => void;
}

type Stage = "idle" | "uploading" | "embedding" | "ready";

export default function DocumentUpload({ onDocumentReady }: Props) {
  const [stage, setStage] = useState<Stage>("idle");
  const [filename, setFilename] = useState("");

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setFilename(file.name);

    try {
      // Stage 1 — Upload
      setStage("uploading");
      toast.loading("Uploading document...", { id: "upload" });
      const uploadResult = await uploadDocument(file);
      toast.success("Uploaded successfully", { id: "upload" });

      // Stage 2 — Embed
      setStage("embedding");
      toast.loading("Processing and embedding document...", { id: "embed" });
      await embedDocument(uploadResult.file_id);
      toast.success("Document ready to query!", { id: "embed" });

      // Stage 3 — Ready
      setStage("ready");
      onDocumentReady(uploadResult.file_id, file.name);

    } catch (error) {
      toast.error("Something went wrong. Check the backend.");
      setStage("idle");
    }
  }, [onDocumentReady]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
    disabled: stage !== "idle",
  });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-xl p-10 text-center cursor-pointer
          transition-all duration-200
          ${isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-blue-400"}
          ${stage !== "idle" ? "opacity-60 cursor-not-allowed" : ""}
        `}
      >
        <input {...getInputProps()} />

        {stage === "idle" && (
          <>
            <Upload className="mx-auto mb-3 text-gray-400" size={36} />
            <p className="text-gray-600 font-medium">
              {isDragActive ? "Drop your PDF here" : "Drag & drop a PDF or click to browse"}
            </p>
            <p className="text-gray-400 text-sm mt-1">PDF files only, max 20MB</p>
          </>
        )}

        {stage === "uploading" && (
          <>
            <Loader className="mx-auto mb-3 text-blue-500 animate-spin" size={36} />
            <p className="text-blue-600 font-medium">Uploading {filename}...</p>
          </>
        )}

        {stage === "embedding" && (
          <>
            <Loader className="mx-auto mb-3 text-purple-500 animate-spin" size={36} />
            <p className="text-purple-600 font-medium">Embedding document — this takes a moment...</p>
            <p className="text-gray-400 text-sm mt-1">Chunking text and generating vectors</p>
          </>
        )}

        {stage === "ready" && (
          <>
            <CheckCircle className="mx-auto mb-3 text-green-500" size={36} />
            <p className="text-green-600 font-medium">{filename} is ready</p>
            <p className="text-gray-400 text-sm mt-1">Start asking questions below</p>
          </>
        )}
      </div>
    </div>
  );
}