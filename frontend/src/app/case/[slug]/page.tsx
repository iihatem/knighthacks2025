"use client";

import Dashboard from "@/components/Dashboard";
import { useCaseData } from "@/hooks/useCases";
import { useRAGSearch, useAgentProcess } from "@/hooks/useRAG";
import { useState, useRef, useEffect, use } from "react";
import {
  PaperAirplaneIcon,
  DocumentIcon,
  CheckCircleIcon,
  XCircleIcon,
  PaperClipIcon,
} from "@heroicons/react/24/outline";

interface CasePageProps {
  params: Promise<{
    slug: string;
  }>;
}

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ActionCard {
  id: string;
  type: "email" | "task" | "research" | "document";
  title: string;
  content: string;
  status: "pending" | "approved" | "rejected";
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
  const { search: ragSearch, results: ragResults } = useRAGSearch();
  const {
    process: agentProcess,
    result: agentResult,
    loading: agentLoading,
  } = useAgentProcess();

  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [actionCards, setActionCards] = useState<ActionCard[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  // Get case name from API data
  // The API returns case metadata in case_metadata field
  const caseName = apiCaseData?.case_metadata?.case_name || "Loading case...";
  const caseNumber = apiCaseData?.case_metadata?.case_number || caseId || "";
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
    setChatInput("");
    setIsProcessing(true);

    try {
      // Process with AI agent
      const response = await agentProcess({
        case_id: caseId,
        query: chatInput,
      });

      // Add assistant response
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          response.result.proposed_actions?.[0]?.draft ||
          "I've processed your request. Here's what I found...",
        timestamp: new Date(),
      };

      setChatMessages((prev) => [...prev, assistantMessage]);

      // Create action cards based on response
      if (response.result.proposed_actions) {
        const newCards: ActionCard[] = response.result.proposed_actions.map(
          (action, index) => ({
            id: `${Date.now()}-${index}`,
            type: determineActionType(action.agent),
            title: `${action.agent} - Action Required`,
            content: action.draft,
            status: "pending" as const,
          })
        );
        setActionCards((prev) => [...prev, ...newCards]);
      }
    } catch (error) {
      console.error("Error processing message:", error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          "I apologize, but I encountered an error processing your request. Please try again.",
        timestamp: new Date(),
      };
      setChatMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const determineActionType = (agentName: string): ActionCard["type"] => {
    if (agentName.toLowerCase().includes("communication")) return "email";
    if (agentName.toLowerCase().includes("research")) return "research";
    if (agentName.toLowerCase().includes("record")) return "document";
    return "task";
  };

  const handleApproveAction = (cardId: string) => {
    setActionCards((prev) =>
      prev.map((card) =>
        card.id === cardId ? { ...card, status: "approved" as const } : card
      )
    );
  };

  const handleRejectAction = (cardId: string) => {
    setActionCards((prev) =>
      prev.map((card) =>
        card.id === cardId ? { ...card, status: "rejected" as const } : card
      )
    );
  };

  const getActionIcon = (type: ActionCard["type"]) => {
    switch (type) {
      case "email":
        return (
          <svg
            className="h-5 w-5"
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
        );
      case "document":
        return <DocumentIcon className="h-5 w-5" />;
      case "research":
        return (
          <svg
            className="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        );
      default:
        return (
          <svg
            className="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
        );
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
            <div className="flex items-center space-x-3 mt-1">
              <p className="text-sm text-gray-500">{caseNumber}</p>
              {clientName && (
                <>
                  <span className="text-gray-300">•</span>
                  <p className="text-sm text-gray-500">Client: {clientName}</p>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Chat Interface - Centered */}
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-3xl shadow-sm border border-gray-200 p-6">
            {/* Chat Messages */}
            <div className="mb-4 max-h-96 overflow-y-auto space-y-4">
              {chatMessages.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p className="text-lg font-medium mb-2">
                    Type here to get started...
                  </p>
                  <p className="text-sm">
                    Ask me to draft emails, research case law, organize files,
                    or schedule meetings.
                  </p>
                </div>
              ) : (
                chatMessages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                        message.role === "user"
                          ? "bg-orange-500 text-white"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">
                        {message.content}
                      </p>
                      <p
                        className={`text-xs mt-1 ${
                          message.role === "user"
                            ? "text-orange-100"
                            : "text-gray-500"
                        }`}
                      >
                        {message.timestamp.toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>
                  </div>
                ))
              )}
              {isProcessing && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-2xl px-4 py-3">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: "0.1s" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      ></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Chat Input */}
            <div className="flex items-center space-x-3">
              <button className="p-3 text-gray-400 hover:text-gray-600 transition-colors">
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
                placeholder="Type here..."
                className="flex-1 px-4 py-3 bg-gray-50 rounded-full border border-gray-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                disabled={isProcessing}
              />
              <button
                onClick={handleSendMessage}
                disabled={isProcessing || !chatInput.trim()}
                className="p-3 bg-orange-500 text-white rounded-full hover:bg-orange-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <PaperAirplaneIcon className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Action Cards - Below Chat */}
        {actionCards.length > 0 && (
          <div className="max-w-4xl mx-auto space-y-4">
            <h2 className="text-lg font-semibold text-gray-800">
              Researched for 3 mins...
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {actionCards.map((card) => (
                <div
                  key={card.id}
                  className="bg-white rounded-2xl shadow-sm border border-gray-200 p-4"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <div className="p-2 bg-orange-100 rounded-lg text-orange-600">
                        {getActionIcon(card.type)}
                      </div>
                      <div>
                        <h3 className="font-medium text-gray-800 text-sm">
                          {card.title}
                        </h3>
                      </div>
                    </div>
                  </div>

                  <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                    {card.content}
                  </p>

                  {card.status === "pending" && (
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleApproveAction(card.id)}
                        className="flex-1 flex items-center justify-center space-x-1 px-3 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm"
                      >
                        <CheckCircleIcon className="h-4 w-4" />
                        <span>Approve</span>
                      </button>
                      <button
                        onClick={() => handleRejectAction(card.id)}
                        className="flex-1 flex items-center justify-center space-x-1 px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-sm"
                      >
                        <XCircleIcon className="h-4 w-4" />
                        <span>Reject</span>
                      </button>
                    </div>
                  )}

                  {card.status === "approved" && (
                    <div className="flex items-center space-x-2 text-green-600 text-sm">
                      <CheckCircleIcon className="h-5 w-5" />
                      <span className="font-medium">Approved</span>
                    </div>
                  )}

                  {card.status === "rejected" && (
                    <div className="flex items-center space-x-2 text-red-600 text-sm">
                      <XCircleIcon className="h-5 w-5" />
                      <span className="font-medium">Rejected</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Organized Files Section */}
        {apiCaseData && apiCaseData.total_chunks > 1 && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">
                Organized {apiCaseData.total_chunks} files for Salesforce
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {apiCaseData.data.slice(0, 8).map((chunk, index) => (
                  <div
                    key={index}
                    className="flex flex-col items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                  >
                    <DocumentIcon className="h-12 w-12 text-gray-400 mb-2" />
                    <p className="text-xs text-gray-600 text-center truncate w-full">
                      {chunk.source_url.split("/").pop() || "Document"}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </Dashboard>
  );
}
