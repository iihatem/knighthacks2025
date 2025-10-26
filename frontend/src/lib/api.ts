/**
 * API service layer for interacting with the backend
 * Base URL: http://localhost:5001
 */

import {
  CreateCaseRequest,
  CreateCaseResponse,
  AddFilesRequest,
  AddFilesResponse,
  ListCasesResponse,
  ViewCaseDataResponse,
  RAGSearchRequest,
  RAGSearchResponse,
  AgentProcessRequest,
  AgentProcessResponse,
  SnowflakeDebugResponse,
  EmbeddingTestResponse,
} from "@/types/case";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";

/**
 * Helper function to handle API errors
 */
const handleApiError = async (response: Response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({
      message: `HTTP ${response.status}: ${response.statusText}`,
    }));
    throw new Error(errorData.message || "An error occurred");
  }
  return response;
};

// ============================================
// 1. CASE MANAGEMENT APIs
// ============================================

/**
 * Create a new case with client metadata and optional files
 * POST /api/create-case
 */
export const createCase = async (
  data: CreateCaseRequest
): Promise<CreateCaseResponse> => {
  const formData = new FormData();
  formData.append("case_name", data.case_name);
  formData.append("client_name", data.client_name);

  if (data.client_phone) {
    formData.append("client_phone", data.client_phone);
  }
  if (data.client_email) {
    formData.append("client_email", data.client_email);
  }
  if (data.files && data.files.length > 0) {
    data.files.forEach((file) => {
      formData.append("files", file);
    });
  }

  const response = await fetch(`${API_BASE_URL}/api/create-case`, {
    method: "POST",
    body: formData,
  });

  await handleApiError(response);
  return response.json();
};

/**
 * Add files to an existing case
 * POST /api/add-case-files
 */
export const addCaseFiles = async (
  data: AddFilesRequest
): Promise<AddFilesResponse> => {
  const formData = new FormData();
  formData.append("case_id", data.case_id);

  data.files.forEach((file) => {
    formData.append("files", file);
  });

  const response = await fetch(`${API_BASE_URL}/api/add-case-files`, {
    method: "POST",
    body: formData,
  });

  await handleApiError(response);
  return response.json();
};

/**
 * List all cases with metadata
 * GET /api/list-cases
 */
export const listCases = async (): Promise<ListCasesResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/list-cases`, {
    method: "GET",
  });

  await handleApiError(response);
  return response.json();
};

/**
 * View all data for a specific case
 * GET /api/view-case-data/:case_id
 */
export const viewCaseData = async (
  caseId: string
): Promise<ViewCaseDataResponse> => {
  const response = await fetch(
    `${API_BASE_URL}/api/view-case-data/${caseId}`,
    {
      method: "GET",
    }
  );

  await handleApiError(response);
  return response.json();
};

// ============================================
// 2. RAG & SEARCH APIs
// ============================================

/**
 * Search case knowledge base using semantic similarity
 * POST /api/test-rag
 */
export const ragSearch = async (
  data: RAGSearchRequest
): Promise<RAGSearchResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/test-rag`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  await handleApiError(response);
  return response.json();
};

// ============================================
// 3. AI AGENT APIs
// ============================================

/**
 * Process a task using the AI orchestrator
 * POST /api/agent/process
 */
export const processWithAgent = async (
  data: AgentProcessRequest
): Promise<AgentProcessResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/agent/process`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  await handleApiError(response);
  return response.json();
};

// ============================================
// 4. DEBUG & TESTING APIs
// ============================================

/**
 * Test Snowflake connection and configuration
 * GET /api/debug/snowflake
 */
export const debugSnowflake = async (): Promise<SnowflakeDebugResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/debug/snowflake`, {
    method: "GET",
  });

  await handleApiError(response);
  return response.json();
};

/**
 * Test Snowflake embedding function
 * GET /api/test-embedding
 */
export const testEmbedding = async (): Promise<EmbeddingTestResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/test-embedding`, {
    method: "GET",
  });

  await handleApiError(response);
  return response.json();
};

/**
 * Health check - verify server is running
 * GET /
 */
export const healthCheck = async (): Promise<string> => {
  const response = await fetch(`${API_BASE_URL}/`, {
    method: "GET",
  });

  await handleApiError(response);
  return response.text();
};

// ============================================
// 5. ACTIVITY MANAGEMENT APIs
// ============================================

/**
 * Get activities for a specific case
 * GET /api/activities/<case_id>
 */
export const getActivities = async (
  caseId: string,
  status?: string
): Promise<any> => {
  const url = status
    ? `${API_BASE_URL}/api/activities/${caseId}?status=${status}`
    : `${API_BASE_URL}/api/activities/${caseId}`;

  const response = await fetch(url, {
    method: "GET",
  });

  await handleApiError(response);
  return response.json();
};

/**
 * Approve an activity
 * POST /api/activities/<activity_id>/approve
 */
export const approveActivity = async (
  activityId: string,
  approvedBy: string
): Promise<any> => {
  const response = await fetch(
    `${API_BASE_URL}/api/activities/${activityId}/approve`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        approved_by: approvedBy,
      }),
    }
  );

  await handleApiError(response);
  return response.json();
};

/**
 * Reject an activity
 * POST /api/activities/<activity_id>/reject
 */
export const rejectActivity = async (
  activityId: string,
  approvedBy: string,
  reason: string
): Promise<any> => {
  const response = await fetch(
    `${API_BASE_URL}/api/activities/${activityId}/reject`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        approved_by: approvedBy,
        reason: reason,
      }),
    }
  );

  await handleApiError(response);
  return response.json();
};

/**
 * Get all pending activities across all cases
 * GET /api/activities/pending
 */
export const getPendingActivities = async (): Promise<any> => {
  const response = await fetch(`${API_BASE_URL}/api/activities/pending`, {
    method: "GET",
  });

  await handleApiError(response);
  return response.json();
};

// ============================================
// 5. UTILITY FUNCTIONS
// ============================================

/**
 * Format case number for display
 */
export const formatCaseNumber = (caseNumber: string): string => {
  return caseNumber;
};

/**
 * Format file count for display
 */
export const formatFileCount = (chunkCount: number): string => {
  if (chunkCount <= 1) {
    return "No files";
  }
  return `${chunkCount} documents`;
};

/**
 * Get similarity score interpretation
 */
export const getSimilarityInterpretation = (
  score: number
): { label: string; color: string } => {
  if (score >= 0.9) {
    return { label: "Extremely relevant", color: "text-green-600" };
  } else if (score >= 0.7) {
    return { label: "Highly relevant", color: "text-blue-600" };
  } else if (score >= 0.5) {
    return { label: "Moderately relevant", color: "text-yellow-600" };
  } else {
    return { label: "Weakly relevant", color: "text-gray-600" };
  }
};

/**
 * Check if case has files
 */
export const caseHasFiles = (chunkCount: number, firstFile: string): boolean => {
  return chunkCount > 1 && firstFile !== "metadata-only";
};

