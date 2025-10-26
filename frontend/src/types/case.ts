/**
 * Type definitions for case-related data structures
 */

export interface Case {
  case_id: string;
  case_number: string;
  case_name: string;
  client_name: string;
  client_phone: string | null;
  client_email: string | null;
  chunk_count: number;
  first_file: string;
}

export interface CaseData {
  case_id: string;
  source_url: string;
  text_chunk: string;
  text_length: number;
  vector_size: number;
}

export interface RAGResult {
  text_chunk: string;
  source_url: string;
  similarity_score: number;
}

export interface CreateCaseRequest {
  case_name: string;
  client_name: string;
  client_phone?: string;
  client_email?: string;
  files?: File[];
}

export interface CreateCaseResponse {
  message: string;
  case_id: string;
  case_number: string;
  files_processed?: number;
}

export interface AddFilesRequest {
  case_id: string;
  files: File[];
}

export interface AddFilesResponse {
  message: string;
  case_id: string;
  files_processed: number;
}

export interface ListCasesResponse {
  total_cases: number;
  cases: Case[];
}

export interface ViewCaseDataResponse {
  case_id: string;
  case_metadata: {
    case_number: string;
    case_name: string;
    client_name: string;
    client_phone: string | null;
    client_email: string | null;
  };
  total_chunks: number;
  data: CaseData[];
}

export interface RAGSearchRequest {
  case_id: string;
  query: string;
  top_k?: number;
}

export interface RAGSearchResponse {
  case_id: string;
  query: string;
  results_count: number;
  results: RAGResult[];
}

export interface AgentProcessRequest {
  case_id: string;
  query: string;
}

export interface AgentProcessResponse {
  status: string;
  result: {
    orchestrator_analysis?: string;
    delegated_to?: string;
    proposed_actions?: Array<{
      agent: string;
      draft: string;
      requires_approval: boolean;
    }>;
  };
}

export interface SnowflakeDebugResponse {
  status: string;
  message: string;
  env_variables: Record<string, string>;
  connection_info?: {
    user: string;
    role: string;
    database: string;
    schema: string;
  };
  case_data_rows?: number;
}

export interface EmbeddingTestResponse {
  status: string;
  message: string;
  test_embedding?: {
    text: string;
    vector_dimensions: number;
    first_5_values: number[];
    last_5_values: number[];
  };
  database_status?: {
    total_rows: number;
    rows_with_vectors: number;
    rows_without_vectors: number;
    sample: any;
  };
  diagnosis?: {
    embedding_works: boolean;
    data_exists: boolean;
    vectors_stored: boolean;
    issue: string | null;
  };
}

