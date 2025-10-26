"use client";

import Dashboard from "@/components/Dashboard";
import { useCaseData } from "@/hooks/useCases";
import { useState, useRef, useEffect, use } from "react";
import { 
  PaperAirplaneIcon, 
  PaperClipIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  SparklesIcon,
  XMarkIcon,
  EnvelopeIcon,
  CalendarIcon,
  MagnifyingGlassIcon,
  DocumentTextIcon,
} from "@heroicons/react/24/outline";
import { processWithAgent, getActivities, approveActivity, rejectActivity } from "@/lib/api";

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

  const { caseData: apiCaseData, loading, error } = useCaseData(caseId || "");

  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [pendingActivities, setPendingActivities] = useState<any[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [selectedActivity, setSelectedActivity] = useState<any | null>(null);
  const [showActivityModal, setShowActivityModal] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  // Fetch pending activities with polling
  useEffect(() => {
    if (caseId) {
      fetchPendingActivities();
      const interval = setInterval(fetchPendingActivities, 5000);
      return () => clearInterval(interval);
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

  const caseName = apiCaseData?.case_metadata?.case_name || caseId;
  const clientName = apiCaseData?.case_metadata?.client_name || "";

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
      const response = await processWithAgent({
        case_id: caseId,
        query: currentInput,
        session_id: sessionId || undefined,
      });

      if (response.session_id) {
        setSessionId(response.session_id);
      }

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          typeof response.result === "string"
            ? response.result
            : typeof response.message === "string"
            ? response.message
            : JSON.stringify(response.result || response, null, 2),
        timestamp: new Date(),
        action_type: response.action_type,
        requires_approval: response.requires_approval,
        activity_id: response.activity_id,
      };

      setChatMessages((prev) => [...prev, assistantMessage]);

      // Refresh activities if approval needed
      if (response.requires_approval) {
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
      
      const systemMessage: ChatMessage = {
        id: Date.now().toString(),
        role: "system",
        content: "✅ Action approved and executed!",
        timestamp: new Date(),
      };
      setChatMessages((prev) => [...prev, systemMessage]);

      await fetchPendingActivities();
      setShowActivityModal(false);
      setSelectedActivity(null);
    } catch (error) {
      console.error("Error approving activity:", error);
      alert("Failed to approve activity");
    }
  };

  const handleReject = async (activityId: string, reason: string) => {
    try {
      await rejectActivity(activityId, "lawyer@firm.com", reason);

      const systemMessage: ChatMessage = {
        id: Date.now().toString(),
        role: "system",
        content: "❌ Action rejected.",
        timestamp: new Date(),
      };
      setChatMessages((prev) => [...prev, systemMessage]);

      await fetchPendingActivities();
      setShowActivityModal(false);
      setSelectedActivity(null);
    } catch (error) {
      console.error("Error rejecting activity:", error);
      alert("Failed to reject activity");
    }
  };

  const openActivityModal = (activity: any) => {
    setSelectedActivity(activity);
    setShowActivityModal(true);
  };

  const getActivityIcon = (actionType: string) => {
    switch (actionType) {
      case "draft_email":
        return <EnvelopeIcon className="h-5 w-5" />;
      case "schedule_appointment":
        return <CalendarIcon className="h-5 w-5" />;
      case "research_external":
        return <MagnifyingGlassIcon className="h-5 w-5" />;
      case "process_evidence":
        return <DocumentTextIcon className="h-5 w-5" />;
      default:
        return <ClockIcon className="h-5 w-5" />;
    }
  };

  const getActivityTitle = (actionType: string) => {
    switch (actionType) {
      case "draft_email":
        return "Draft Email";
      case "schedule_appointment":
        return "Schedule Appointment";
      case "research_external":
        return "External Research";
      case "process_evidence":
        return "Process Evidence";
      default:
        return actionType?.replace(/_/g, " ").toUpperCase() || "Action";
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
      <div className="h-full flex flex-col space-y-4 overflow-hidden">
        {/* Compact Header */}
        <div className="flex-shrink-0">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-gray-900">{caseName}</h1>
              {clientName && (
                <p className="text-sm text-gray-600 mt-0.5">Client: {clientName}</p>
              )}
            </div>
            <span className="px-3 py-1 bg-green-50 text-green-700 rounded-full text-xs font-semibold border border-green-200">
              Active
            </span>
          </div>
        </div>

        {/* Chat Interface - Clean Design */}
        <div className="flex-1 bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden flex flex-col">
          {/* Chat Header */}
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center">
                <SparklesIcon className="h-5 w-5 text-white" />
              </div>
              <div>
                <h2 className="text-sm font-semibold text-gray-900">AI Legal Assistant</h2>
                <p className="text-xs text-gray-500">Powered by Gemini AI</p>
              </div>
            </div>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 px-6 py-4 overflow-y-auto">
            {chatMessages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mb-4">
                  <SparklesIcon className="h-8 w-8 text-orange-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Start a conversation
                </h3>
                <p className="text-sm text-gray-600 max-w-md">
                  Ask me to research case law, draft emails, schedule appointments, or analyze case details.
                </p>
              </div>
            )}

            <div className="space-y-4">
              {chatMessages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-lg px-4 py-3 rounded-lg ${
                      message.role === "user"
                        ? "bg-orange-600 text-white"
                        : message.role === "system"
                        ? "bg-green-50 text-green-900 border border-green-200"
                        : "bg-gray-100 text-gray-900"
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    <span className={`block text-right text-xs mt-1 ${
                      message.role === "user" ? "text-orange-200" : "text-gray-500"
                    }`}>
                      {message.timestamp.toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                    {message.requires_approval && (
                      <div className="mt-2 pt-2 border-t border-gray-300">
                        <p className="text-xs font-semibold text-orange-600 flex items-center">
                          <ClockIcon className="h-3 w-3 mr-1" />
                          Awaiting approval
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {isProcessing && (
                <div className="flex justify-start">
                  <div className="px-4 py-3 rounded-lg bg-gray-100">
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-orange-500 rounded-full animate-bounce"></div>
                        <div
                          className="w-2 h-2 bg-orange-500 rounded-full animate-bounce"
                          style={{ animationDelay: "0.1s" }}
                        ></div>
                        <div
                          className="w-2 h-2 bg-orange-500 rounded-full animate-bounce"
                          style={{ animationDelay: "0.2s" }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-700">AI is thinking...</span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={chatEndRef} />
            </div>
          </div>

          {/* Chat Input */}
          <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
            <div className="flex items-center space-x-3">
              <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors">
                <PaperClipIcon className="h-5 w-5" />
              </button>
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
                placeholder="Ask me anything about this case..."
                className="flex-1 px-4 py-2 bg-white rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm"
                disabled={isProcessing}
              />
              <button
                onClick={handleSendMessage}
                disabled={isProcessing || !chatInput.trim()}
                className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
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

        {/* Pending Approvals - Horizontal Cards */}
        {pendingActivities.length > 0 && (
          <div className="flex-shrink-0 animate-fadeIn">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold text-gray-900">Pending Approvals</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {pendingActivities.map((activity) => (
                <div
                  key={activity.activity_id}
                  className="bg-white border-2 border-orange-200 rounded-lg p-4 hover:shadow-lg hover:border-orange-400 transition-all duration-200 transform hover:scale-105 cursor-pointer"
                  onClick={() => openActivityModal(activity)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center text-orange-600">
                        {getActivityIcon(activity.agent_action)}
                      </div>
                      <div className="flex-1">
                        <h3 className="text-sm font-semibold text-gray-900">
                          {getActivityTitle(activity.agent_action)}
                        </h3>
                        <p className="text-xs text-gray-500">Click to review</p>
                      </div>
                    </div>
                    <ClockIcon className="h-5 w-5 text-orange-500 flex-shrink-0 animate-pulse" />
                  </div>
                  
                  <p className="text-xs text-gray-600 line-clamp-2 mb-3">
                    {activity.prompt || "No description"}
                  </p>

                  <div className="text-xs text-gray-400">
                    {new Date(activity.created_at).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Activity Modal */}
        {showActivityModal && selectedActivity && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn" onClick={() => setShowActivityModal(false)}>
            <div 
              className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-hidden animate-slideUp"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-gradient-to-r from-orange-50 to-orange-100">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center text-white">
                    {getActivityIcon(selectedActivity.agent_action)}
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-gray-900">
                      {getActivityTitle(selectedActivity.agent_action)}
                    </h2>
                    <p className="text-xs text-gray-600">
                      {new Date(selectedActivity.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setShowActivityModal(false)}
                  className="p-2 hover:bg-orange-200 rounded-lg transition-colors"
                >
                  <XMarkIcon className="h-5 w-5 text-gray-600" />
                </button>
              </div>

              {/* Modal Content */}
              <div className="px-6 py-4 overflow-y-auto max-h-96">
                <div className="space-y-4">
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Request:</h3>
                    <p className="text-sm text-gray-900 bg-gray-50 p-3 rounded-lg border border-gray-200">
                      {selectedActivity.prompt}
                    </p>
                  </div>

                  {selectedActivity.agent_response && (
                    <div>
                      <h3 className="text-sm font-semibold text-gray-700 mb-2">
                        {selectedActivity.agent_action === "draft_email" ? "Email Draft:" : "Details:"}
                      </h3>
                      <div className="text-sm text-gray-900 bg-gray-50 p-3 rounded-lg border border-gray-200 whitespace-pre-wrap">
                        {typeof selectedActivity.agent_response === 'string' 
                          ? selectedActivity.agent_response 
                          : JSON.stringify(selectedActivity.agent_response, null, 2)}
                      </div>
                    </div>
                  )}

                  {selectedActivity.action_data && (
                    <div>
                      <h3 className="text-sm font-semibold text-gray-700 mb-2">Action Data:</h3>
                      <div className="space-y-2">
                        {selectedActivity.action_data.to && (
                          <div className="flex items-center space-x-2 text-sm">
                            <span className="font-medium text-gray-700">To:</span>
                            <span className="text-gray-900">{selectedActivity.action_data.to}</span>
                          </div>
                        )}
                        {selectedActivity.action_data.subject && (
                          <div className="flex items-center space-x-2 text-sm">
                            <span className="font-medium text-gray-700">Subject:</span>
                            <span className="text-gray-900">{selectedActivity.action_data.subject}</span>
                          </div>
                        )}
                        {selectedActivity.action_data.draft && (
                          <div className="text-sm">
                            <span className="font-medium text-gray-700 block mb-1">Message:</span>
                            <div className="text-gray-900 bg-white p-3 rounded-lg border border-gray-200 whitespace-pre-wrap">
                              {selectedActivity.action_data.draft}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Modal Actions */}
              <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-end space-x-3">
                <button
                  onClick={() => setShowActivityModal(false)}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    const reason = prompt("Reason for rejection:");
                    if (reason) handleReject(selectedActivity.activity_id, reason);
                  }}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium flex items-center space-x-2"
                >
                  <XCircleIcon className="h-5 w-5" />
                  <span>Reject</span>
                </button>
                <button
                  onClick={() => handleApprove(selectedActivity.activity_id)}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium flex items-center space-x-2"
                >
                  <CheckCircleIcon className="h-5 w-5" />
                  <span>Approve</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Dashboard>
  );
}
