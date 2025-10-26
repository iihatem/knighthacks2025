"use client";

import Dashboard from "@/components/Dashboard";
import Link from "next/link";
import AddCaseModal from "@/components/AddCaseModal";
import { useState } from "react";
import { useCases } from "@/hooks/useCases";

export default function CasesPage() {
  const [isAddCaseModalOpen, setIsAddCaseModalOpen] = useState(false);
  const { cases, loading, error, refetch } = useCases();

  return (
    <Dashboard>
      <div className="space-y-6">
        {/* Cases Header */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h1 className="text-2xl font-bold text-gray-800 mb-2">Legal Cases</h1>
          <p className="text-gray-600">
            Manage and track all your legal cases with Briefly.
          </p>
        </div>

        {/* Cases Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
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
                  {loading ? "..." : cases.length}
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
                  With Metadata
                </p>
                <p className="text-2xl font-semibold text-gray-900">
                  {loading
                    ? "..."
                    : cases.filter((c) => c.case_name !== null).length}
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
                    d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                  />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Clients</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {loading
                    ? "..."
                    : new Set(
                        cases
                          .filter((c) => c.client_name)
                          .map((c) => c.client_name)
                      ).size}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-lg">
                <svg
                  className="h-6 w-6 text-purple-600"
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
                  {loading
                    ? "..."
                    : cases.reduce((sum, c) => sum + (c.chunk_count || 0), 0)}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Cases List */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Recent Cases</h3>
            <button
              onClick={() => setIsAddCaseModalOpen(true)}
              className="px-4 py-2 bg-orange-500 text-white rounded-full hover:bg-orange-600 transition-colors duration-200 flex items-center space-x-2"
            >
              <svg
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                />
              </svg>
              <span className="text-sm font-medium">Add Case</span>
            </button>
          </div>
          <div className="p-6 max-h-[400px] overflow-y-auto">
            <div className="space-y-4">
              {loading ? (
                <p className="text-gray-600">Loading cases...</p>
              ) : error ? (
                <p className="text-red-500">Error: {error}</p>
              ) : cases.length === 0 ? (
                <p className="text-gray-600">
                  No cases found. Create your first case!
                </p>
              ) : (
                cases.map((caseItem) => (
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
                          {caseItem.client_name && (
                            <p className="text-sm text-gray-600">
                              Client: {caseItem.client_name}
                            </p>
                          )}
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
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Add Case Modal */}
      <AddCaseModal
        isOpen={isAddCaseModalOpen}
        onClose={() => setIsAddCaseModalOpen(false)}
        onSuccess={() => {
          refetch(); // Refresh the cases list
        }}
      />
    </Dashboard>
  );
}
