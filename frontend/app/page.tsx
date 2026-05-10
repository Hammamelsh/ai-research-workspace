"use client";

import { useState } from "react";
import { Toaster } from "react-hot-toast";
import DocumentUpload from "@/components/DocumentUpload";
import ChatInterface from "@/components/ChatInterface";
import { Brain } from "lucide-react";

export default function Home() {
  const [activeDoc, setActiveDoc] = useState<{
    fileId: string;
    filename: string;
  } | null>(null);

  return (
    <main className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />

      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center gap-3">
          <Brain className="text-blue-600" size={28} />
          <div>
            <h1 className="text-xl font-bold text-gray-900">AI Research Workspace</h1>
            <p className="text-gray-500 text-sm">Upload documents, ask questions, get cited answers</p>
          </div>
        </div>
      </header>

      {/* Main content */}
      <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">

        {/* Upload section */}
        <section>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
            1. Upload Document
          </h2>
          <DocumentUpload
            onDocumentReady={(fileId, filename) =>
              setActiveDoc({ fileId, filename })
            }
          />
        </section>

        {/* Chat section */}
        {activeDoc && (
          <section>
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
              2. Ask Questions
            </h2>
            <ChatInterface
              fileId={activeDoc.fileId}
              filename={activeDoc.filename}
            />
          </section>
        )}

        {!activeDoc && (
          <div className="text-center py-12 text-gray-400">
            <p className="text-sm">Upload a document above to start asking questions</p>
          </div>
        )}
      </div>
    </main>
  );
}