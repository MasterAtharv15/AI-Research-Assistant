import { useState } from 'react';

import { uploadPdf } from '../services/api';
import type { UploadResponse } from '../types/api';

interface UploadProps {
  onUploadSuccess?: (filename: string) => void;
}

export default function Upload({ onUploadSuccess }: UploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const [uploadedFilename, setUploadedFilename] = useState<string>('');

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;

    if (file && file.type !== 'application/pdf') {
      setSelectedFile(null);
      setErrorMessage('Please choose a PDF file.');
      setSuccessMessage('');
      return;
    }

    setSelectedFile(file);
    setErrorMessage('');
    setSuccessMessage('');
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setErrorMessage('Please select a PDF file first.');
      return;
    }

    setIsUploading(true);
    setErrorMessage('');
    setSuccessMessage('');

    try {
      const result = await uploadPdf(selectedFile);
      setUploadResult(result);
      setUploadedFilename(result.filename);
      setSuccessMessage(`Upload complete for ${result.filename}.`);
      onUploadSuccess?.(result.filename);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Upload failed.';
      setErrorMessage(message);
      setUploadResult(null);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <section style={{ maxWidth: '480px', margin: '2rem auto', padding: '1rem', border: '1px solid #ddd', borderRadius: '8px' }}>
      <h2>Upload PDF</h2>
      <p>Select a PDF document to prepare it for the AI research assistant.</p>

      <input
        type="file"
        accept="application/pdf"
        onChange={handleFileChange}
      />

      <div style={{ marginTop: '0.75rem' }}>
        <strong>Selected file:</strong> {selectedFile ? selectedFile.name : 'No file selected'}
      </div>

      <button
        type="button"
        onClick={handleUpload}
        disabled={!selectedFile || isUploading}
        style={{ marginTop: '0.75rem', padding: '0.5rem 1rem' }}
      >
        {isUploading ? 'Uploading...' : 'Upload PDF'}
      </button>

      {errorMessage ? <p style={{ color: 'crimson', marginTop: '0.75rem' }}>{errorMessage}</p> : null}
      {successMessage ? <p style={{ color: 'green', marginTop: '0.75rem' }}>{successMessage}</p> : null}

      {uploadResult ? (
        <div style={{ marginTop: '1rem' }}>
          <h3>Upload Summary</h3>
          <p><strong>Filename:</strong> {uploadedFilename}</p>
          <p><strong>Chunks:</strong> {uploadResult.num_chunks}</p>
          <p><strong>Characters:</strong> {uploadResult.num_characters}</p>
        </div>
      ) : null}
    </section>
  );
}
