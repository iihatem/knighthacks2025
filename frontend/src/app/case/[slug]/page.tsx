"use client";

import Dashboard from "@/components/Dashboard";
import ApprovalCard from "@/components/ApprovalCard";
import { useCaseData } from "@/hooks/useCases";
import { useState, useRef, useEffect, use } from "react";
import { PaperAirplaneIcon, PaperClipIcon } from "@heroicons/react/24/outline";
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
      <div className="space-y-6">
        {/* Case Title - Small, Top Left */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold text-gray-800">
              {displayCaseName}
            </h1>
            {clientName && (
              <p className="text-sm text-gray-500 mt-1">Client: {clientName}</p>
            )}
          </div>
        </div>

        {/* Chat Interface - Centered */}
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-3xl shadow-sm border border-gray-200 p-6">
            {/* Chat Messages */}
            <div className="h-96 overflow-y-auto mb-4 space-y-4">
              {chatMessages.length === 0 && (
                <div className="text-center text-gray-500 mt-10">
                  <p className="text-lg font-medium mb-2">
                    👋 Hi! I'm your AI legal assistant
                  </p>
                  <p className="text-sm">
                    Ask me to research case law, draft emails, schedule
                    appointments, or anything else!
                  </p>
                  <div className="mt-6 text-left bg-gray-50 rounded-lg p-4">
                    <p className="text-sm font-medium text-gray-700 mb-2">
                      Try asking:
                    </p>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>• "What injuries did the client suffer?"</li>
                      <li>
                        • "Draft an email to the client about the settlement"
                      </li>
                      <li>
                        • "Schedule a meeting with the client for Thursday"
                      </li>
                      <li>• "Research similar slip and fall cases"</li>
                    </ul>
                  </div>
                </div>
              )}

              {chatMessages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${
                      message.role === "user"
                        ? "bg-orange-500 text-white"
                        : message.role === "system"
                        ? "bg-gray-200 text-gray-800 italic"
                        : "bg-gray-100 text-gray-800"
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                    <span
                      className={`block text-right text-xs mt-1 ${
                        message.role === "user"
                          ? "text-orange-100"
                          : "text-gray-500"
                      }`}
                    >
                      {message.timestamp.toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                    {message.requires_approval && (
                      <div className="mt-2 pt-2 border-t border-gray-300">
                        <p className="text-xs text-orange-600 font-medium">
                          ⚠️ Approval required - see below
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {isProcessing && (
                <div className="flex justify-start">
                  <div className="max-w-xs lg:max-w-md px-4 py-3 rounded-2xl bg-gray-100 text-gray-800">
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                        <div
                          className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                          style={{ animationDelay: "0.1s" }}
                        ></div>
                        <div
                          className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                          style={{ animationDelay: "0.2s" }}
                        ></div>
                      </div>
                      <span className="text-sm">AI is thinking...</span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={chatEndRef} />
            </div>

            {/* Chat Input */}
            <div className="flex items-center space-x-3 border-t border-gray-200 pt-4">
              <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                <PaperClipIcon className="h-6 w-6" />
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
                placeholder="Ask me to research, draft emails, schedule appointments..."
                className="flex-1 px-4 py-3 bg-gray-50 rounded-full border border-gray-200 focus:outline-none focus:ring-2 focus:ring-orange-500 text-gray-800"
                disabled={isProcessing}
              />
              <button
                onClick={handleSendMessage}
                className="p-3 bg-orange-500 text-white rounded-full hover:bg-orange-600 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={isProcessing || !chatInput.trim()}
              >
                <PaperAirplaneIcon className="h-6 w-6" />
              </button>
            </div>
          </div>
        </div>

        {/* Pending Approvals */}
        {pendingActivities.length > 0 && (
          <div className="max-w-4xl mx-auto">
            <h2 className="text-xl font-bold text-gray-800 mb-4">
              ⚠️ Actions Awaiting Your Approval
            </h2>
            {pendingActivities.map((activity) => (
              <ApprovalCard
                key={activity.activity_id}
                activity={activity}
                onApprove={() => handleApprove(activity.activity_id)}
                onReject={(reason) =>
                  handleReject(activity.activity_id, reason)
                }
              />
            ))}
          </div>
        )}
      </div>
    </Dashboard>
  );
}
