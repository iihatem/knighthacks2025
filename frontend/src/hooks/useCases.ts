/**
 * React hooks for case management
 */

import { useState, useEffect, useCallback } from "react";
import { listCases, viewCaseData, createCase, addCaseFiles } from "@/lib/api";
import type {
  Case,
  CreateCaseRequest,
  AddFilesRequest,
  ViewCaseDataResponse,
} from "@/types/case";

/**
 * Hook to fetch and manage all cases
 */
export const useCases = () => {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCases = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await listCases();
      setCases(response.cases);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch cases");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCases();
  }, [fetchCases]);

  return { cases, loading, error, refetch: fetchCases };
};

/**
 * Hook to fetch a single case's data
 */
export const useCaseData = (caseId: string | null) => {
  const [caseData, setCaseData] = useState<ViewCaseDataResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCaseData = useCallback(async () => {
    if (!caseId) return;

    setLoading(true);
    setError(null);
    try {
      const response = await viewCaseData(caseId);
      setCaseData(response);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to fetch case data"
      );
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    fetchCaseData();
  }, [fetchCaseData]);

  return { caseData, loading, error, refetch: fetchCaseData };
};

/**
 * Hook to create a new case
 */
export const useCreateCase = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const create = useCallback(async (data: CreateCaseRequest) => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      const response = await createCase(data);
      setSuccess(true);
      return response;
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to create case";
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setError(null);
    setSuccess(false);
  }, []);

  return { create, loading, error, success, reset };
};

/**
 * Hook to add files to an existing case
 */
export const useAddCaseFiles = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const addFiles = useCallback(async (data: AddFilesRequest) => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      const response = await addCaseFiles(data);
      setSuccess(true);
      return response;
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to add files";
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setError(null);
    setSuccess(false);
  }, []);

  return { addFiles, loading, error, success, reset };
};

