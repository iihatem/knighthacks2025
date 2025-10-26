/**
 * React hooks for RAG (Retrieval-Augmented Generation) search
 */

import { useState, useCallback } from "react";
import { ragSearch, processWithAgent } from "@/lib/api";
import type {
  RAGSearchRequest,
  RAGSearchResponse,
  AgentProcessRequest,
  AgentProcessResponse,
} from "@/types/case";

/**
 * Hook to perform RAG search on case knowledge base
 */
export const useRAGSearch = () => {
  const [results, setResults] = useState<RAGSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async (data: RAGSearchRequest) => {
    setLoading(true);
    setError(null);
    try {
      const response = await ragSearch(data);
      setResults(response);
      return response;
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to perform search";
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResults(null);
    setError(null);
  }, []);

  return { search, results, loading, error, reset };
};

/**
 * Hook to process tasks with AI agent
 */
export const useAgentProcess = () => {
  const [result, setResult] = useState<AgentProcessResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const process = useCallback(async (data: AgentProcessRequest) => {
    setLoading(true);
    setError(null);
    try {
      const response = await processWithAgent(data);
      setResult(response);
      return response;
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to process with agent";
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { process, result, loading, error, reset };
};

