"use client";

import Dashboard from "@/components/Dashboard";
import Link from "next/link";
import { useCases } from "@/hooks/useCases";
import { use, useMemo } from "react";

interface ClientPageProps {
  params: Promise<{
    slug: string;
  }>;
}

export default function ClientPage({ params }: ClientPageProps) {
  const { slug } = use(params);
  const clientName = decodeURIComponent(slug);
  const { cases, loading, error } = useCases();

  // Filter cases for this specific client
  const clientCases = useMemo(() => {
    if (!cases || cases.length === 0) return [];
    return cases.filter(
      (caseItem) =>
        caseItem.client_name &&
        caseItem.client_name.toLowerCase() === clientName.toLowerCase()
    );
  }, [cases, clientName]);

  // Get client info from first case
  const clientInfo = clientCases.length > 0 ? clientCases[0] : null;

  if (loading) {
    return (
      <Dashboard>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-600">Loading client...</div>
        </div>
      </Dashboard>
    );
  }

  if (error) {
    return (
      <Dashboard>
        <div className="flex items-center justify-center h-64">
          <div className="text-red-600">Error loading client: {error}</div>
        </div>
      </Dashboard>
    );
  }

  if (clientCases.length === 0) {
    return (
      <Dashboard>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-600">Client not found.</div>
        </div>
      </Dashboard>
    );
  }

  // Generate initials
  const initials = clientName
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <Dashboard>
      <div className="space-y-6">
        {/* Client Header */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-4">
            <div className="w-20 h-20 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center">
              <span className="text-white text-2xl font-semibold">
                {initials}
              </span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">{clientName}</h1>
              <div className="flex items-center space-x-3 mt-1">
                {clientInfo?.client_email && (
                  <p className="text-sm text-gray-600">
                    {clientInfo.client_email}
                  </p>
                )}
                {clientInfo?.client_phone && (
                  <>
                    {clientInfo.client_email && (
                      <span className="text-gray-300">•</span>
                    )}
                    <p className="text-sm text-gray-600">
                      {clientInfo.client_phone}
                    </p>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Client Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-3 bg-orange-100 rounded-lg">
                <svg
                  className="h-6 w-6 text-orange-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Cases</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {clientCases.length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-lg">
                <svg
                  className="h-6 w-6 text-green-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">
                  Active Cases
                </p>
                <p className="text-2xl font-semibold text-gray-900">
                  {clientCases.length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-lg">
                <svg
                  className="h-6 w-6 text-blue-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Files</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {clientCases.reduce(
                    (sum, c) => sum + (c.chunk_count || 0),
                    0
                  )}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Client Cases */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Cases for {clientName}
            </h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {clientCases.map((caseItem) => (
                <Link
                  href={`/case/${caseItem.case_id}`}
                  key={caseItem.case_id}
                  className="block"
                >
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors duration-200 cursor-pointer">
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center mr-4">
                        <svg
                          className="h-5 w-5 text-white"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                          />
                        </svg>
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900">
                          {caseItem.case_name || caseItem.case_id}
                        </h4>
                        <p className="text-sm text-gray-600">
                          {caseItem.chunk_count || 0} file
                          {caseItem.chunk_count !== 1 ? "s" : ""}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="px-2 py-1 bg-orange-100 text-orange-700 text-xs rounded-full">
                        Active
                      </span>
                      <svg
                        className="h-4 w-4 text-gray-400"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </Dashboard>
  );
}
