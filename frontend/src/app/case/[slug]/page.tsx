import Dashboard from "@/components/Dashboard";
import { notFound } from "next/navigation";

interface CasePageProps {
  params: {
    slug: string;
  };
}

// Sample case data - in a real app, this would come from an API
const caseData: Record<string, any> = {
  "personal-injury-case": {
    title: "Personal Injury Case",
    client: "John Smith",
    status: "Active",
    type: "Personal Injury",
    filedDate: "2 days ago",
    description:
      "Motor vehicle accident case involving rear-end collision on Highway 101.",
    priority: "High",
    documents: 12,
    lastActivity: "2 hours ago",
  },
  "contract-dispute": {
    title: "Contract Dispute",
    client: "ABC Corp",
    status: "Pending",
    type: "Contract Law",
    filedDate: "1 week ago",
    description:
      "Breach of contract dispute regarding software development agreement.",
    priority: "Medium",
    documents: 8,
    lastActivity: "1 day ago",
  },
  "employment-law": {
    title: "Employment Law",
    client: "Jane Doe",
    status: "Completed",
    type: "Employment Law",
    filedDate: "2 weeks ago",
    description: "Wrongful termination case settled out of court.",
    priority: "Low",
    documents: 15,
    lastActivity: "1 week ago",
  },
  "johnson-vs-abc-corp": {
    title: "Johnson vs. ABC Corp",
    client: "Johnson",
    status: "Active",
    type: "Contract Dispute",
    filedDate: "2 days ago",
    description: "Contract dispute regarding payment terms and deliverables.",
    priority: "High",
    documents: 6,
    lastActivity: "4 hours ago",
  },
  "smith-estate-planning": {
    title: "Smith Estate Planning",
    client: "Smith Family",
    status: "Completed",
    type: "Estate Law",
    filedDate: "1 week ago",
    description:
      "Comprehensive estate planning including will and trust documents.",
    priority: "Medium",
    documents: 22,
    lastActivity: "3 days ago",
  },
  "davis-personal-injury": {
    title: "Davis Personal Injury",
    client: "Davis",
    status: "Urgent",
    type: "Personal Injury",
    filedDate: "3 days ago",
    description:
      "Slip and fall accident at commercial property requiring immediate attention.",
    priority: "Urgent",
    documents: 4,
    lastActivity: "1 hour ago",
  },
};

export default function CasePage({ params }: CasePageProps) {
  const caseInfo = caseData[params.slug];

  if (!caseInfo) {
    notFound();
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "active":
        return "bg-green-100 text-green-800";
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      case "completed":
        return "bg-blue-100 text-blue-800";
      case "urgent":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case "urgent":
        return "bg-red-100 text-red-800";
      case "high":
        return "bg-orange-100 text-orange-800";
      case "medium":
        return "bg-yellow-100 text-yellow-800";
      case "low":
        return "bg-green-100 text-green-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <Dashboard>
      <div className="space-y-6">
        {/* Case Header */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-800 mb-2">
                {caseInfo.title}
              </h1>
              <p className="text-gray-600 mb-4">{caseInfo.description}</p>
              <div className="flex items-center space-x-4">
                <div>
                  <span className="text-sm text-gray-500">Client:</span>
                  <span className="ml-2 font-medium text-gray-800">
                    {caseInfo.client}
                  </span>
                </div>
                <div>
                  <span className="text-sm text-gray-500">Type:</span>
                  <span className="ml-2 font-medium text-gray-800">
                    {caseInfo.type}
                  </span>
                </div>
                <div>
                  <span className="text-sm text-gray-500">Filed:</span>
                  <span className="ml-2 font-medium text-gray-800">
                    {caseInfo.filedDate}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex flex-col items-end space-y-2">
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
                  caseInfo.status
                )}`}
              >
                {caseInfo.status}
              </span>
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(
                  caseInfo.priority
                )}`}
              >
                {caseInfo.priority} Priority
              </span>
            </div>
          </div>
        </div>

        {/* Case Stats */}
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
                <p className="text-sm font-medium text-gray-600">Documents</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {caseInfo.documents}
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
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">
                  Last Activity
                </p>
                <p className="text-2xl font-semibold text-gray-900">
                  {caseInfo.lastActivity}
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
                    d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Progress</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {caseInfo.status === "Completed" ? "100%" : "75%"}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Case Details */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Case Details
          </h3>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">
                  Case ID
                </label>
                <p className="text-gray-800">
                  {params.slug.toUpperCase().replace(/-/g, "-")}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">
                  Assigned Attorney
                </label>
                <p className="text-gray-800">Sarah Johnson, Esq.</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">
                  Court
                </label>
                <p className="text-gray-800">Superior Court of California</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">
                  Next Hearing
                </label>
                <p className="text-gray-800">
                  {caseInfo.status === "Completed"
                    ? "N/A"
                    : "December 15, 2024"}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Recent Activity
          </h3>
          <div className="space-y-4">
            <div className="flex items-start">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-3 mt-1">
                <svg
                  className="h-4 w-4 text-green-600"
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
              <div className="flex-1">
                <p className="text-sm text-gray-800">
                  <span className="font-medium">Document uploaded</span> -
                  Medical records and police report
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {caseInfo.lastActivity}
                </p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3 mt-1">
                <svg
                  className="h-4 w-4 text-blue-600"
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
              <div className="flex-1">
                <p className="text-sm text-gray-800">
                  <span className="font-medium">Email sent</span> to client
                  regarding case updates
                </p>
                <p className="text-xs text-gray-500 mt-1">1 day ago</p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center mr-3 mt-1">
                <svg
                  className="h-4 w-4 text-orange-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-800">
                  <span className="font-medium">Court filing</span> - Motion for
                  summary judgment submitted
                </p>
                <p className="text-xs text-gray-500 mt-1">3 days ago</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Dashboard>
  );
}
