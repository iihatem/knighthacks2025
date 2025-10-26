import Dashboard from "@/components/Dashboard";

export default function Home() {
  return (
    <Dashboard>
      <div className="space-y-6">
        {/* Income Tracker Card */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center mr-3">
                <svg
                  className="h-5 w-5 text-orange-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-800">Case Tracker</h2>
            </div>
            <select className="px-3 py-2 bg-gray-100 rounded-lg text-sm text-gray-600 border-0 focus:outline-none focus:ring-2 focus:ring-orange-500">
              <option>Week</option>
              <option>Month</option>
              <option>Year</option>
            </select>
          </div>
          <p className="text-gray-600 mb-6">
            Track changes in case progress over time and access detailed data on
            each case and outcomes.
          </p>

          {/* Chart placeholder */}
          <div className="mb-6">
            <div className="flex items-end justify-between h-32">
              {["S", "M", "T", "W", "T", "F", "S"].map((day, index) => (
                <div key={day} className="flex flex-col items-center">
                  <div
                    className={`w-8 h-16 bg-gray-200 rounded-t-lg mb-2 ${
                      index === 2 ? "bg-orange-500" : "bg-gray-200"
                    }`}
                  ></div>
                  <span className="text-xs text-gray-500">{day}</span>
                  {index === 2 && (
                    <span className="text-xs text-orange-600 font-medium mt-1">
                      $2,567
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center">
            <span className="text-2xl font-bold text-orange-600 mr-2">
              +20%
            </span>
            <span className="text-gray-600">
              This week's cases are higher than last week's
            </span>
          </div>
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Cases */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800">
                Your Recent Cases
              </h3>
              <a href="#" className="text-orange-600 text-sm font-medium">
                See all Cases
              </a>
            </div>

            <div className="space-y-4">
              <div className="flex items-center p-3 bg-gray-50 rounded-xl">
                <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center mr-3">
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
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-800">
                      $10/hour
                    </span>
                    <span className="px-2 py-1 bg-gray-800 text-white text-xs rounded-full">
                      Active
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                      Remote
                    </span>
                    <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                      Part-time
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    Contract Law Case
                  </p>
                  <p className="text-xs text-gray-500">New York • 2h ago</p>
                </div>
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
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </div>

              <div className="flex items-center p-3 bg-gray-50 rounded-xl">
                <div className="w-10 h-10 bg-gray-600 rounded-lg flex items-center justify-center mr-3">
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
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-800">
                      $10/hour
                    </span>
                    <span className="px-2 py-1 bg-gray-200 text-gray-700 text-xs rounded-full">
                      Pending
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    Copyright Dispute
                  </p>
                  <p className="text-xs text-gray-500">California • 4h ago</p>
                </div>
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
                    d="M5 15l7-7 7 7"
                  />
                </svg>
              </div>

              <div className="flex items-center p-3 bg-gray-50 rounded-xl">
                <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center mr-3">
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
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-800">
                      $10/hour
                    </span>
                    <span className="px-2 py-1 bg-gray-800 text-white text-xs rounded-full">
                      Active
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    Web Design Contract
                  </p>
                  <p className="text-xs text-gray-500">Texas • 6h ago</p>
                </div>
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
                    d="M5 15l7-7 7 7"
                  />
                </svg>
              </div>
            </div>
          </div>

          {/* Let's Connect */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800">
                Let's Connect
              </h3>
              <a href="#" className="text-orange-600 text-sm font-medium">
                See all
              </a>
            </div>

            <div className="space-y-4">
              <div className="flex items-center p-3 bg-gray-50 rounded-xl">
                <div className="w-12 h-12 bg-gray-300 rounded-full flex items-center justify-center mr-3">
                  <svg
                    className="h-6 w-6 text-gray-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                    />
                  </svg>
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-gray-800">
                      Randy Gouse
                    </span>
                    <span className="px-2 py-1 bg-orange-100 text-orange-700 text-xs rounded-full">
                      Senior
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">
                    Cybersecurity specialist
                  </p>
                </div>
                <button className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
                  <svg
                    className="h-4 w-4 text-white"
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
                </button>
              </div>

              <div className="flex items-center p-3 bg-gray-50 rounded-xl">
                <div className="w-12 h-12 bg-gray-300 rounded-full flex items-center justify-center mr-3">
                  <svg
                    className="h-6 w-6 text-gray-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                    />
                  </svg>
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-gray-800">
                      Giana Schleifer
                    </span>
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                      Middle
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">UX/UI Designer</p>
                </div>
                <button className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
                  <svg
                    className="h-4 w-4 text-white"
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
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Unlock Premium Features */}
          <div className="bg-gradient-to-r from-orange-50 to-orange-100 rounded-2xl shadow-sm border border-orange-200 p-6 relative overflow-hidden">
            <div className="relative z-10">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                Unlock Premium Features
              </h3>
              <p className="text-gray-600 mb-4">
                Get access to exclusive benefits and expand your legal practice
                opportunities.
              </p>
              <button className="px-6 py-3 bg-white text-gray-800 rounded-full font-medium hover:bg-gray-50 transition-colors duration-200 flex items-center">
                Upgrade now
                <svg
                  className="h-4 w-4 ml-2"
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
              </button>
            </div>
            <div className="absolute top-0 right-0 w-32 h-32 opacity-10">
              <div className="w-full h-full bg-orange-500 rounded-full"></div>
            </div>
          </div>

          {/* Case Progress */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800">
                Case Progress
              </h3>
              <div className="flex items-center text-sm text-gray-600">
                <svg
                  className="h-4 w-4 mr-1"
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
                April 11, 2024
                <svg
                  className="h-4 w-4 ml-1"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-800 mb-1">64</div>
                <div className="text-sm text-gray-600 mb-2">Cases filed</div>
                <div className="flex justify-center space-x-1">
                  {[...Array(8)].map((_, i) => (
                    <div key={i} className="w-1 h-4 bg-gray-300 rounded"></div>
                  ))}
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-800 mb-1">12</div>
                <div className="text-sm text-gray-600 mb-2">Interviews</div>
                <div className="flex justify-center space-x-1">
                  {[...Array(6)].map((_, i) => (
                    <div key={i} className="w-1 h-4 bg-red-400 rounded"></div>
                  ))}
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-800 mb-1">10</div>
                <div className="text-sm text-gray-600 mb-2">Wins</div>
                <div className="flex justify-center space-x-1">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="w-1 h-4 bg-gray-800 rounded"></div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Dashboard>
  );
}
