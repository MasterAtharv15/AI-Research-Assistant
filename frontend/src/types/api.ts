export interface UploadResponse {
  filename: string;
  extracted_text: string;
  num_characters: number;
  num_chunks: number;
  first_chunk: string;
}

export interface QueryRequest {
  filename: string;
  query: string;
  session_id?: string | null;
}

export interface Match {
  chunk_id: number;
  text: string;
}

export interface QueryResponse {
  session_id: string;
  query: string;
  answer: string;
  matches: Match[];
}
