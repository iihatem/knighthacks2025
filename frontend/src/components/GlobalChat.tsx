"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  PaperAirplaneIcon,
  PaperClipIcon,
  XMarkIcon,
  ChevronDownIcon,
  ChevronUpIcon,
} from "@heroicons/react/24/outline";
import { processWithAgent } from "@/lib/api";
import { useCases } from "@/hooks/useCases";
import ApprovalCard from "@/components/ApprovalCard";
import { getActivities, approveActivity, rejectActivity } from "@/lib/api";

interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  action_type?: string;
  requires_approval?: boolean;
  activity_id?: string;
}

const GlobalChat: React.FC = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [pendingActivities, setPendingActivities] = useState<any[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [attachments, setAttachments] = useState<File[]>([]);

  const chatEndRef = useRef<HTMLDivElement>(null);
  const { cases, loading: casesLoading } = useCases();

  // Auto-scroll to bottom of chat
  useEffect(() => {
    if (isExpanded) {
      chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatMessages, isExpanded]);

  // Auto-select first case if none selected
  useEffect(() => {
    if (!selectedCaseId && cases.length > 0) {
      setSelectedCaseId(cases[0].case_id);
    }
  }, [cases, selectedCaseId]);

  const fetchPendingActivities = async (caseId: string) => {
    try {
      const response = await getActivities(caseId, "pending");
      setPendingActivities(response.activities || []);
    } catch (error) {
      console.error("Error fetching activities:", error);
    }
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim() || isProcessing) return;

    // If no case selected, prompt user
    if (!selectedCaseId) {
      alert("Please select a case first");
      return;
    }

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
        case_id: selectedCaseId,
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
            : JSON.stringify(response.result, null, 2),
        timestamp: new Date(),
        action_type: response.action_type,
        requires_approval: response.requires_approval,
        activity_id: response.activity_id,
      };

      setChatMessages((prev) => [...prev, assistantMessage]);

      if (response.requires_approval && response.activity_logged) {
        await fetchPendingActivities(selectedCaseId);
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

      if (selectedCaseId) {
        await fetchPendingActivities(selectedCaseId);
      }
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
        content: "❌ Action rejected. You can ask me to revise it.",
        timestamp: new Date(),
      };
      setChatMessages((prev) => [...prev, systemMessage]);

      if (selectedCaseId) {
        await fetchPendingActivities(selectedCaseId);
      }
    } catch (error) {
      console.error("Error rejecting activity:", error);
      alert("Failed to reject activity");
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setAttachments((prev) => [...prev, ...files]);
  };

  const removeAttachment = (index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 w-96">
      {/* Expanded Chat Window */}
      {isExpanded && (
        <div className="bg-white rounded-2xl shadow-2xl border border-gray-200 mb-4 overflow-hidden">
          {/* Header */}
          <div className="bg-orange-500 text-white p-4 flex items-center justify-between">
            <div>
              <h3 className="font-semibold">AI Legal Assistant</h3>
              <p className="text-xs text-orange-100">
                {selectedCaseId ? "Connected to case" : "No case selected"}
              </p>
            </div>
            <button
              onClick={() => setIsExpanded(false)}
              className="p-1 hover:bg-orange-600 rounded"
            >
              <ChevronDownIcon className="h-5 w-5" />
            </button>
          </div>

          {/* Case Selector */}
          <div className="p-3 border-b border-gray-200 bg-gray-50">
            <label className="text-xs font-medium text-gray-700 block mb-1">
              Select Case:
            </label>
            <select
              value={selectedCaseId || ""}
              onChange={(e) => setSelectedCaseId(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              disabled={casesLoading}
            >
              {casesLoading ? (
                <option>Loading cases...</option>
              ) : cases.length === 0 ? (
                <option>No cases available</option>
              ) : (
                cases.map((caseItem) => (
                  <option key={caseItem.case_id} value={caseItem.case_id}>
                    {caseItem.case_name || caseItem.case_id}
                  </option>
                ))
              )}
            </select>
          </div>

          {/* Chat Messages */}
          <div className="h-96 overflow-y-auto p-4 space-y-3">
            {chatMessages.length === 0 && (
              <div className="text-center text-gray-500 mt-10">
                <p className="text-sm font-medium mb-2">
                  👋 Hi! I'm your AI assistant
                </p>
                <p className="text-xs">
                  Ask me to research, draft emails, or schedule appointments!
                </p>
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
                  className={`max-w-xs px-3 py-2 rounded-2xl text-sm ${
                    message.role === "user"
                      ? "bg-orange-500 text-white"
                      : message.role === "system"
                      ? "bg-gray-200 text-gray-800 italic"
                      : "bg-gray-100 text-gray-800"
                  }`}
                >
                  <p className="whitespace-pre-wrap break-words">
                    {message.content}
                  </p>
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
                    <div className="mt-1 pt-1 border-t border-gray-300">
                      <p className="text-xs text-orange-600 font-medium">
                        ⚠️ Approval required
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isProcessing && (
              <div className="flex justify-start">
                <div className="max-w-xs px-3 py-2 rounded-2xl bg-gray-100 text-gray-800">
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
                    <span className="text-xs">Thinking...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Pending Approvals */}
          {pendingActivities.length > 0 && (
            <div className="border-t border-gray-200 p-3 bg-yellow-50 max-h-48 overflow-y-auto">
              <p className="text-xs font-semibold text-gray-700 mb-2">
                ⚠️ {pendingActivities.length} Pending Approval(s)
              </p>
              {pendingActivities.map((activity) => (
                <div
                  key={activity.activity_id}
                  className="text-xs bg-white p-2 rounded mb-2"
                >
                  <p className="font-medium">{activity.agent_action}</p>
                  <div className="flex space-x-2 mt-1">
                    <button
                      onClick={() => handleApprove(activity.activity_id)}
                      className="px-2 py-1 bg-green-500 text-white rounded text-xs"
                    >
                      ✓ Approve
                    </button>
                    <button
                      onClick={() =>
                        handleReject(activity.activity_id, "Rejected from chat")
                      }
                      className="px-2 py-1 bg-red-500 text-white rounded text-xs"
                    >
                      ✗ Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Attachments */}
          {attachments.length > 0 && (
            <div className="p-3 border-t border-gray-200 bg-gray-50">
              <div className="flex flex-wrap gap-2">
                {attachments.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center bg-orange-100 rounded-full px-2 py-1 text-xs"
                  >
                    <span className="truncate max-w-32">{file.name}</span>
                    <button
                      onClick={() => removeAttachment(index)}
                      className="ml-1"
                    >
                      <XMarkIcon className="h-3 w-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="p-3 border-t border-gray-200 bg-white">
            <div className="flex items-center space-x-2">
              <label className="cursor-pointer p-2 hover:bg-gray-100 rounded">
                <PaperClipIcon className="h-5 w-5 text-gray-400" />
                <input
                  type="file"
                  multiple
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </label>
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
                placeholder="Type your message..."
                className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-orange-500"
                disabled={isProcessing || !selectedCaseId}
              />
              <button
                onClick={handleSendMessage}
                className="p-2 bg-orange-500 text-white rounded-full hover:bg-orange-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={isProcessing || !chatInput.trim() || !selectedCaseId}
              >
                <PaperAirplaneIcon className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Floating Button */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-14 h-14 bg-orange-500 text-white rounded-full shadow-lg hover:bg-orange-600 transition-all duration-200 flex items-center justify-center"
      >
        {isExpanded ? (
          <ChevronDownIcon className="h-6 w-6" />
        ) : (
          <svg
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
            />
          </svg>
        )}
      </button>
    </div>
  );
};

export default GlobalChat;
