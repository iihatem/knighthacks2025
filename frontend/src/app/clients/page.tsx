"use client";

import Dashboard from "@/components/Dashboard";
import Link from "next/link";
import { useCases } from "@/hooks/useCases";
import { useMemo } from "react";

export default function ClientsPage() {
  const { cases, loading, error } = useCases();

  // Extract unique clients from cases
  const clients = useMemo(() => {
    if (!cases || cases.length === 0) return [];

    const clientMap = new Map();
    cases.forEach((caseItem) => {
      if (caseItem.client_name) {
        const key = caseItem.client_name;
        if (!clientMap.has(key)) {
          clientMap.set(key, {
            name: caseItem.client_name,
            email: caseItem.client_email,
            phone: caseItem.client_phone,
            cases: [],
          });
        }
        clientMap.get(key).cases.push({
          case_id: caseItem.case_id,
          case_name: caseItem.case_name,
          case_number: caseItem.case_number,
        });
      }
    });

    return Array.from(clientMap.values());
  }, [cases]);

  const totalClients = clients.length;
  const clientsWithEmail = clients.filter((c) => c.email).length;
  const clientsWithPhone = clients.filter((c) => c.phone).length;
  const clientsWithMultipleCases = clients.filter(
    (c) => c.cases.length > 1
  ).length;

  return (
    <Dashboard>
      <div className="space-y-6">
        {/* Clients Header */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h1 className="text-2xl font-bold text-gray-800 mb-2">
            Client Management
          </h1>
          <p className="text-gray-600">
            Manage your client relationships and track communication history.
          </p>
        </div>

        {/* Client Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
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
                <p className="text-sm font-medium text-gray-600">
                  Total Clients
                </p>
                <p className="text-2xl font-semibold text-gray-900">
                  {loading ? "..." : totalClients}
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
                    d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">With Email</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {loading ? "..." : clientsWithEmail}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-3 bg-yellow-100 rounded-lg">
                <svg
                  className="h-6 w-6 text-yellow-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                  />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">With Phone</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {loading ? "..." : clientsWithPhone}
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
                <p className="text-sm font-medium text-gray-600">
                  Multiple Cases
                </p>
                <p className="text-2xl font-semibold text-gray-900">
                  {loading ? "..." : clientsWithMultipleCases}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Clients List */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">All Clients</h3>
          </div>
          <div className="p-6 max-h-[600px] overflow-y-auto">
            <div className="space-y-4">
              {loading ? (
                <p className="text-gray-600">Loading clients...</p>
              ) : error ? (
                <p className="text-red-500">Error: {error}</p>
              ) : clients.length === 0 ? (
                <p className="text-gray-600">
                  No clients found. Create a case to add clients.
                </p>
              ) : (
                clients.map((client, index) => {
                  // Generate initials from name
                  const initials = client.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")
                    .toUpperCase()
                    .slice(0, 2);

                  // Cycle through colors for variety
                  const colors = [
                    "bg-orange-500",
                    "bg-blue-500",
                    "bg-green-500",
                    "bg-purple-500",
                    "bg-pink-500",
                    "bg-indigo-500",
                  ];
                  const colorClass = colors[index % colors.length];

                  return (
                    <Link
                      href={`/client/${encodeURIComponent(client.name)}`}
                      key={client.name}
                      className="block"
                    >
                      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors duration-200 cursor-pointer">
                        <div className="flex items-center flex-1">
                          <div
                            className={`w-12 h-12 ${colorClass} rounded-full flex items-center justify-center mr-4`}
                          >
                            <span className="text-white font-medium text-lg">
                              {initials}
                            </span>
                          </div>
                          <div className="flex-1">
                            <h4 className="font-medium text-gray-900">
                              {client.name}
                            </h4>
                            <div className="flex items-center space-x-2 mt-1">
                              {client.email && (
                                <p className="text-sm text-gray-600">
                                  {client.email}
                                </p>
                              )}
                              {client.phone && (
                                <>
                                  {client.email && (
                                    <span className="text-gray-300">•</span>
                                  )}
                                  <p className="text-sm text-gray-600">
                                    {client.phone}
                                  </p>
                                </>
                              )}
                            </div>
                            <p className="text-xs text-gray-500 mt-1">
                              {client.cases.length} case
                              {client.cases.length !== 1 ? "s" : ""}
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
                  );
                })
              )}
            </div>
          </div>
        </div>
      </div>
    </Dashboard>
  );
}
