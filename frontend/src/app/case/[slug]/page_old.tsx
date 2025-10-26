"use client";

import Dashboard from "@/components/Dashboard";
import ApprovalCard from "@/components/ApprovalCard";
import { useCaseData } from "@/hooks/useCases";
import { useState, useRef, useEffect, use } from "react";
import { 
  PaperAirplaneIcon, 
  PaperClipIcon,
  EnvelopeIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  SparklesIcon,
  MagnifyingGlassIcon,
  CalendarIcon,
  FolderIcon,
  ArrowDownTrayIcon
} from "@heroicons/react/24/outline";
import { processWithAgent } from "@/lib/api";
import { getActivities, approveActivity, rejectActivity } from "@/lib/api";

interface CasePageProps {
  params: Promise<{
    slug: string;
  }>;
}

interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  action_type?: string;
  requires_approval?: boolean;
  activity_id?: string;
}

export default function CasePage({ params }: CasePageProps) {
  const { slug } = use(params);
  const caseId = slug;

  // Early return if no caseId
  if (!caseId) {
    return (
      <Dashboard>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-600">Loading case...</div>
        </div>
      </Dashboard>
    );
  }

  const { caseData: apiCaseData, loading, error } = useCaseData(caseId);

  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [pendingActivities, setPendingActivities] = useState<any[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  // Fetch pending activities on mount
  useEffect(() => {
    if (caseId) {
      fetchPendingActivities();
    }
  }, [caseId]);

  const fetchPendingActivities = async () => {
    try {
      const response = await getActivities(caseId, "pending");
      setPendingActivities(response.activities || []);
    } catch (error) {
      console.error("Error fetching activities:", error);
    }
  };

  // Get case name from API data
  const caseName = apiCaseData?.case_metadata?.case_name || "Loading case...";
  const clientName = apiCaseData?.case_metadata?.client_name || "";

  // Format case display name with null safety
  const displayCaseName =
    caseName !== "Loading case..."
      ? caseName
      : caseId
      ? caseId.replace("case-", "Case ")
      : "Loading...";

  const handleSendMessage = async () => {
    if (!chatInput.trim() || isProcessing) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: chatInput,
      timestamp: new Date(),
    };

    setChatMessages((prev) => [...prev, userMessage]);
    const currentInput = chatInput;
    setChatInput("");
    setIsProcessing(true);

    try {
      // Call the real API
      const response = await processWithAgent({
        case_id: caseId,
        query: currentInput,
        session_id: sessionId || undefined,
      });

      // Update session ID
      if (response.session_id) {
        setSessionId(response.session_id);
      }

      // Add AI response to chat
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          typeof response.result === "string"
            ? response.result
            : JSON.stringify(response.result, null, 2),
        timestamp: new Date(),
        action_type: response.action_type,
        requires_approval: response.requires_approval,
        activity_id: response.activity_id,
      };

      setChatMessages((prev) => [...prev, assistantMessage]);

      // If requires approval, fetch updated activities
      if (response.requires_approval && response.activity_logged) {
        await fetchPendingActivities();
      }
    } catch (error) {
      console.error("Error processing message:", error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "system",
        content: `Error: ${
          error instanceof Error ? error.message : "Failed to process message"
        }`,
        timestamp: new Date(),
      };
      setChatMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleApprove = async (activityId: string) => {
    try {
      await approveActivity(activityId, "lawyer@firm.com");

      // Add system message
      const systemMessage: ChatMessage = {
        id: Date.now().toString(),
        role: "system",
        content: "✅ Action approved and executed!",
        timestamp: new Date(),
      };
      setChatMessages((prev) => [...prev, systemMessage]);

      // Refresh activities
      await fetchPendingActivities();
    } catch (error) {
      console.error("Error approving activity:", error);
      alert("Failed to approve activity");
    }
  };

  const handleReject = async (activityId: string, reason: string) => {
    try {
      await rejectActivity(activityId, "lawyer@firm.com", reason);

      // Add system message
      const systemMessage: ChatMessage = {
        id: Date.now().toString(),
        role: "system",
        content: "❌ Action rejected. You can ask me to revise it.",
        timestamp: new Date(),
      };
      setChatMessages((prev) => [...prev, systemMessage]);

      // Refresh activities
      await fetchPendingActivities();
    } catch (error) {
      console.error("Error rejecting activity:", error);
      alert("Failed to reject activity");
    }
  };

  if (loading) {
    return (
      <Dashboard>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-600">Loading case...</div>
        </div>
      </Dashboard>
    );
  }

  if (error) {
    return (
      <Dashboard>
        <div className="flex items-center justify-center h-64">
          <div className="text-red-600">Error loading case: {error}</div>
        </div>
      </Dashboard>
    );
  }

  return (
    <Dashboard>
      <div className="h-full flex flex-col overflow-hidden">
        {/* Top: Case Header - Compact */}
        <div className="flex-shrink-0 mb-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-orange-600 to-orange-500 bg-clip-text text-transparent">
                {displayCaseName}
              </h1>
              {clientName && (
                <p className="text-sm text-gray-600 mt-0.5">Client: {clientName}</p>
              )}
            </div>
            <div className="flex items-center space-x-2">
              <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-semibold flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-2"></div>
                Active
              </span>
            </div>
          </div>
        </div>

        {/* Main Content: Three Column Layout */}
        <div className="flex-1 grid grid-cols-12 gap-4 overflow-hidden">
          
          {/* LEFT COLUMN: Agentic Action Panels (3/12) */}
          <div className="col-span-3 space-y-3 overflow-y-auto">
            
            {/* Download Case Records Panel */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-4 border-2 border-blue-200 hover:border-blue-400 transition-all duration-300 cursor-pointer group">
              <div className="flex items-start justify-between mb-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                  <FolderIcon className="h-5 w-5 text-white" />
                </div>
                <ArrowDownTrayIcon className="h-5 w-5 text-blue-400 group-hover:text-blue-600 transition-colors" />
              </div>
              <h3 className="text-sm font-bold text-gray-800 mb-1">Download Case Records</h3>
              <p className="text-xs text-gray-600 mb-3">Access all case files, documents, and evidence</p>
              <button className="w-full px-3 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg text-xs font-semibold hover:shadow-lg transition-all duration-200 transform hover:scale-105">
                View Records
              </button>
            </div>

            {/* Send Email to Client Panel */}
            <div className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-2xl p-4 border-2 border-orange-200 hover:border-orange-400 transition-all duration-300 cursor-pointer group">
              <div className="flex items-start justify-between mb-3">
                <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-amber-600 rounded-xl flex items-center justify-center shadow-lg">
                  <EnvelopeIcon className="h-5 w-5 text-white" />
                </div>
                <SparklesIcon className="h-5 w-5 text-orange-400 group-hover:text-orange-600 transition-colors animate-pulse" />
              </div>
              <h3 className="text-sm font-bold text-gray-800 mb-1">Send Email to Client</h3>
              <p className="text-xs text-gray-600 mb-3">AI-powered drafts sent for your approval</p>
              <button 
                onClick={() => {
                  setChatInput("Draft an email to the client about the case status");
                  handleSendMessage();
                }}
                className="w-full px-3 py-2 bg-gradient-to-r from-orange-500 to-amber-600 text-white rounded-lg text-xs font-semibold hover:shadow-lg transition-all duration-200 transform hover:scale-105"
              >
                Draft Email
              </button>
            </div>

            {/* AI Research Panel */}
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-4 border-2 border-purple-200 hover:border-purple-400 transition-all duration-300 cursor-pointer group">
              <div className="flex items-start justify-between mb-3">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center shadow-lg">
                  <MagnifyingGlassIcon className="h-5 w-5 text-white" />
                </div>
                <SparklesIcon className="h-5 w-5 text-purple-400 group-hover:text-purple-600 transition-colors animate-pulse" />
              </div>
              <h3 className="text-sm font-bold text-gray-800 mb-1">AI Legal Research</h3>
              <p className="text-xs text-gray-600 mb-3">Search case law and similar precedents</p>
              <button 
                onClick={() => {
                  setChatInput("Research similar cases and relevant case law");
                  handleSendMessage();
                }}
                className="w-full px-3 py-2 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-lg text-xs font-semibold hover:shadow-lg transition-all duration-200 transform hover:scale-105"
              >
                Start Research
              </button>
            </div>

            {/* Pending Approvals Summary */}
            {pendingActivities.length > 0 && (
              <div className="bg-gradient-to-br from-red-50 to-rose-50 rounded-2xl p-4 border-2 border-red-200">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-bold text-gray-800">Pending Approvals</h3>
                  <div className="w-6 h-6 bg-red-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-xs font-bold">{pendingActivities.length}</span>
                  </div>
                </div>
                <p className="text-xs text-gray-600">
                  {pendingActivities.length} action{pendingActivities.length > 1 ? 's' : ''} waiting for your review
                </p>
              </div>
            )}
          </div>

          {/* MIDDLE COLUMN: AI Chat Interface (6/12) */}
          <div className="col-span-6 flex flex-col overflow-hidden">
            <div className="flex-1 bg-white rounded-3xl shadow-xl border-2 border-gray-200 overflow-hidden flex flex-col"
              style={{
                background: "linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(255, 250, 245, 0.98) 100%)",
              }}
            >
              {/* Chat Header */}
              <div 
                className="px-6 py-4 border-b-2"
                style={{
                  background: "linear-gradient(90deg, rgba(255, 87, 51, 0.08) 0%, rgba(255, 140, 0, 0.05) 100%)",
                  borderColor: "rgba(255, 87, 51, 0.1)",
                }}
              >
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center shadow-lg">
                      <SparklesIcon className="h-6 w-6 text-white" />
                    </div>
                    <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white animate-pulse"></div>
                  </div>
                  <div>
                    <h2 className="text-lg font-bold bg-gradient-to-r from-orange-600 to-orange-500 bg-clip-text text-transparent">
                      AI Legal Assistant
                    </h2>
                    <p className="text-xs text-gray-500">Powered by Gemini AI • Multi-Agent Orchestration</p>
                  </div>
                </div>
              </div>

              {/* Chat Messages - Scrollable */}
              <div className="flex-1 px-6 py-4 overflow-y-auto scrollbar-thin scrollbar-thumb-orange-300 scrollbar-track-gray-100">
                {chatMessages.length === 0 && (
                  <div className="flex flex-col items-center justify-center h-full text-center px-8">
                    <div className="w-20 h-20 bg-gradient-to-br from-orange-400 to-orange-600 rounded-2xl flex items-center justify-center shadow-xl mb-4">
                      <SparklesIcon className="h-10 w-10 text-white" />
                    </div>
                    <h3 className="text-xl font-bold text-gray-800 mb-2">
                      👋 Hi! I'm your AI Legal Assistant
                    </h3>
                    <p className="text-sm text-gray-600 mb-6 max-w-md">
                      I can help you research case law, draft emails, schedule appointments, process evidence, and manage case records.
                    </p>
                    
                    {/* Quick Actions */}
                    <div className="grid grid-cols-2 gap-3 w-full max-w-lg">
                      <button 
                        onClick={() => {
                          setChatInput("What injuries did the client suffer?");
                        }}
                        className="px-4 py-3 bg-gradient-to-r from-blue-50 to-blue-100 border-2 border-blue-200 rounded-xl text-left hover:border-blue-400 transition-all duration-200 group"
                      >
                        <p className="text-xs font-semibold text-blue-800 group-hover:text-blue-900">📊 Case Analysis</p>
                        <p className="text-xs text-blue-600 mt-1">Review client injuries</p>
                      </button>
                      <button 
                        onClick={() => {
                          setChatInput("Draft an email to the client about settlement");
                        }}
                        className="px-4 py-3 bg-gradient-to-r from-orange-50 to-orange-100 border-2 border-orange-200 rounded-xl text-left hover:border-orange-400 transition-all duration-200 group"
                      >
                        <p className="text-xs font-semibold text-orange-800 group-hover:text-orange-900">✉️ Draft Email</p>
                        <p className="text-xs text-orange-600 mt-1">Settlement update</p>
                      </button>
                      <button 
                        onClick={() => {
                          setChatInput("Research similar slip and fall cases");
                        }}
                        className="px-4 py-3 bg-gradient-to-r from-purple-50 to-purple-100 border-2 border-purple-200 rounded-xl text-left hover:border-purple-400 transition-all duration-200 group"
                      >
                        <p className="text-xs font-semibold text-purple-800 group-hover:text-purple-900">🔍 Legal Research</p>
                        <p className="text-xs text-purple-600 mt-1">Find precedents</p>
                      </button>
                      <button 
                        onClick={() => {
                          setChatInput("Schedule a meeting with the client for Thursday");
                        }}
                        className="px-4 py-3 bg-gradient-to-r from-green-50 to-green-100 border-2 border-green-200 rounded-xl text-left hover:border-green-400 transition-all duration-200 group"
                      >
                        <p className="text-xs font-semibold text-green-800 group-hover:text-green-900">📅 Schedule</p>
                        <p className="text-xs text-green-600 mt-1">Book appointment</p>
                      </button>
                    </div>
                  </div>
                )}

                <div className="space-y-4">
                  {chatMessages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${
                        message.role === "user" ? "justify-end" : "justify-start"
                      } animate-fadeIn`}
                    >
                      <div
                        className={`max-w-lg px-5 py-3 rounded-2xl shadow-md transition-all duration-200 hover:shadow-lg ${
                          message.role === "user"
                            ? "bg-gradient-to-r from-orange-500 to-orange-600 text-white"
                            : message.role === "system"
                            ? "bg-gradient-to-r from-green-100 to-green-200 text-green-900 border-2 border-green-300"
                            : "bg-white text-gray-800 border-2 border-gray-200"
                        }`}
                      >
                        <p className="whitespace-pre-wrap break-words leading-relaxed text-sm">
                          {message.content}
                        </p>
                        <span
                          className={`block text-right text-xs mt-2 ${
                            message.role === "user"
                              ? "text-orange-100"
                              : "text-gray-400"
                          }`}
                        >
                          {message.timestamp.toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                        {message.requires_approval && (
                          <div className="mt-3 pt-3 border-t border-gray-300">
                            <p className="text-xs font-bold text-orange-600 flex items-center">
                              <ClockIcon className="h-4 w-4 mr-1" />
                              Awaiting your approval
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}

                  {isProcessing && (
                    <div className="flex justify-start animate-fadeIn">
                      <div className="max-w-md px-5 py-4 rounded-2xl bg-gradient-to-r from-gray-50 to-gray-100 border-2 border-gray-200 shadow-md">
                        <div className="flex items-center space-x-3">
                          <div className="flex space-x-1">
                            <div className="w-3 h-3 bg-orange-500 rounded-full animate-bounce"></div>
                            <div
                              className="w-3 h-3 bg-orange-500 rounded-full animate-bounce"
                              style={{ animationDelay: "0.1s" }}
                            ></div>
                            <div
                              className="w-3 h-3 bg-orange-500 rounded-full animate-bounce"
                              style={{ animationDelay: "0.2s" }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium text-gray-700">AI agents are working on your request...</span>
                        </div>
                      </div>
                    </div>
                  )}

                  <div ref={chatEndRef} />
                </div>
              </div>

              {/* Chat Input */}
              <div className="px-6 pb-4 pt-2 border-t-2 border-gray-100">
                <div 
                  className="flex items-center space-x-3 p-2 rounded-2xl border-2 transition-all duration-300 bg-white"
                  style={{
                    borderColor: chatInput.trim() ? "rgba(255, 87, 51, 0.5)" : "rgba(209, 213, 219, 0.5)",
                    boxShadow: chatInput.trim() ? "0 0 0 3px rgba(255, 87, 51, 0.1)" : "none",
                  }}
                >
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                    placeholder="✨ Ask me to research, draft, schedule, or analyze..."
                    className="flex-1 px-4 py-3 rounded-xl border-0 focus:outline-none bg-transparent text-gray-700 placeholder-gray-400 font-medium"
                    disabled={isProcessing}
                  />
                  
                  <button className="p-3 rounded-xl transition-all duration-200 hover:bg-orange-50 group">
                    <PaperClipIcon className="h-5 w-5 text-gray-400 group-hover:text-orange-600 transition-colors" />
                  </button>
                  
                  <button
                    onClick={handleSendMessage}
                    disabled={isProcessing || !chatInput.trim()}
                    className="px-6 py-3 text-white rounded-xl transition-all duration-200 font-semibold disabled:cursor-not-allowed flex items-center space-x-2 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none"
                    style={{ 
                      background: (isProcessing || !chatInput.trim())
                        ? "#9ca3af"
                        : "linear-gradient(135deg, #ff5733 0%, #ff8c00 100%)",
                      opacity: (isProcessing || !chatInput.trim()) ? 0.6 : 1
                    }}
                  >
                    {isProcessing ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        <span className="text-sm">Sending</span>
                      </>
                    ) : (
                      <>
                        <span className="text-sm">Send</span>
                        <PaperAirplaneIcon className="h-4 w-4" />
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN: Pending Approvals (3/12) */}
          <div className="col-span-3 overflow-y-auto">
            <div className="space-y-3">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-sm font-bold text-gray-800">Pending Approvals</h2>
                {pendingActivities.length > 0 && (
                  <div className="px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-bold">
                    {pendingActivities.length}
                  </div>
                )}
              </div>

              {pendingActivities.length === 0 ? (
                <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-6 border-2 border-green-200 text-center">
                  <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-3">
                    <CheckCircleIcon className="h-6 w-6 text-white" />
                  </div>
                  <p className="text-sm font-semibold text-gray-800 mb-1">All Clear!</p>
                  <p className="text-xs text-gray-600">No pending actions</p>
                </div>
              ) : (
                pendingActivities.map((activity) => (
                  <ApprovalCard
                    key={activity.activity_id}
                    activity={activity}
                    onApprove={() => handleApprove(activity.activity_id)}
                    onReject={(reason) => handleReject(activity.activity_id, reason)}
                  />
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </Dashboard>
  );
}
