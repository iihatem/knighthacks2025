"use client";

import React, { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  processWithAgent,
  getActivities,
  approveActivity,
  rejectActivity,
} from "@/lib/api";
import { useCases } from "@/hooks/useCases";
import {
  HomeIcon,
  DocumentTextIcon,
  UserGroupIcon,
  CalendarIcon,
  ChartBarIcon,
  CogIcon,
  BellIcon,
  UserCircleIcon,
  PaperClipIcon,
  XMarkIcon,
  PaperAirplaneIcon,
  MinusIcon,
  ChatBubbleLeftRightIcon,
} from "@heroicons/react/24/outline";

interface DashboardProps {
  children?: React.ReactNode;
}

interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
}

const Dashboard: React.FC<DashboardProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [attachments, setAttachments] = useState<File[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [showCaseSelector, setShowCaseSelector] = useState(false);
  const [isChatMinimized, setIsChatMinimized] = useState(false);

  const pathname = usePathname();
  const { cases, loading: casesLoading } = useCases();
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-select first case if none selected
  useEffect(() => {
    if (!selectedCaseId && cases.length > 0) {
      setSelectedCaseId(cases[0].case_id);
    }
  }, [cases, selectedCaseId]);

  // Auto-scroll in chat messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  const navigationItems = [
    { name: "Dashboard", icon: HomeIcon, href: "/", current: pathname === "/" },
    {
      name: "Cases",
      icon: DocumentTextIcon,
      href: "/cases",
      current: pathname === "/cases",
    },
    {
      name: "Clients",
      icon: UserGroupIcon,
      href: "/clients",
      current: pathname === "/clients",
    },
    {
      name: "Calendar",
      icon: CalendarIcon,
      href: "/calendar",
      current: pathname === "/calendar",
    },
    {
      name: "Analytics",
      icon: ChartBarIcon,
      href: "/analytics",
      current: pathname === "/analytics",
    },
  ];

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setAttachments((prev) => [...prev, ...files]);
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const droppedFiles = Array.from(event.dataTransfer.files);
    setAttachments((prev) => [...prev, ...droppedFiles]);
  };

  const removeAttachment = (index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim() || isProcessing) return;

    if (!selectedCaseId) {
      alert("Please select a case first by clicking on the chat box");
      setShowCaseSelector(true);
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
      };

      setChatMessages((prev) => [...prev, assistantMessage]);
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

  return (
    <div
      className="h-screen flex flex-col overflow-hidden"
      style={{ backgroundColor: "var(--color-bg-primary)" }}
    >
      {/* Main content */}
      <div className="flex flex-col h-full">
        {/* Header */}
        <header
          className="bg-white shadow-sm border-b flex-shrink-0"
          style={{
            backgroundColor: "var(--color-bg-card)",
            borderColor: "var(--color-gray-light)",
          }}
        >
          <div className="flex items-center justify-between h-16 px-6">
            {/* Logo */}
            <div className="w-18 h-18 flex items-center justify-center">
              <img
                src="/briefly_logo.svg"
                alt="Briefly Logo"
                className="w-full h-full"
              />
            </div>

            {/* Navigation Menu - Centered */}
            <nav className="absolute left-1/2 transform -translate-x-1/2 flex space-x-8">
              <Link
                href="/"
                className="font-medium pb-1"
                style={{
                  color:
                    pathname === "/"
                      ? "var(--color-text-primary)"
                      : "var(--color-text-secondary)",
                  borderBottom:
                    pathname === "/"
                      ? "2px solid var(--color-accent-orange)"
                      : "none",
                }}
              >
                Home
              </Link>
              <Link
                href="/cases"
                className="font-medium pb-1"
                style={{
                  color:
                    pathname === "/cases"
                      ? "var(--color-text-primary)"
                      : "var(--color-text-secondary)",
                  borderBottom:
                    pathname === "/cases"
                      ? "2px solid var(--color-accent-orange)"
                      : "none",
                }}
              >
                Cases
              </Link>
              <Link
                href="/clients"
                className="font-medium pb-1"
                style={{
                  color:
                    pathname === "/clients"
                      ? "var(--color-text-primary)"
                      : "var(--color-text-secondary)",
                  borderBottom:
                    pathname === "/clients"
                      ? "2px solid var(--color-accent-orange)"
                      : "none",
                }}
              >
                Clients
              </Link>
            </nav>

            <div className="flex items-center space-x-4">
              <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full">
                <BellIcon className="h-5 w-5" />
              </button>
              <Link href="/settings">
                <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full">
                  <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                    <UserCircleIcon className="h-6 w-6" />
                  </div>
                </button>
              </Link>
            </div>
          </div>
        </header>

        {/* Main content area */}
        <main className="flex-1 p-6 overflow-hidden">{children}</main>

        {/* Floating Chat - Minimized Button (Futuristic) */}
        {isChatMinimized && (
          <div className="fixed bottom-8 right-8 z-40 animate-fadeIn">
            <button
              onClick={() => setIsChatMinimized(false)}
              className="group px-8 py-4 text-white rounded-2xl shadow-2xl hover:shadow-3xl transition-all duration-300 flex items-center space-x-3 font-semibold transform hover:scale-105 border-2 border-orange-400/30"
              style={{
                background: "linear-gradient(135deg, #ff5733 0%, #ff8c00 100%)",
              }}
            >
              <div className="relative">
                <ChatBubbleLeftRightIcon className="h-6 w-6" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full border-2 border-white animate-pulse"></div>
              </div>
              <span className="text-base">
                {selectedCaseId
                  ? `💬 ${
                      cases.find((c) => c.case_id === selectedCaseId)
                        ?.case_name || "Chat"
                    }`
                  : "🤖 Open AI Assistant"}
              </span>
              {chatMessages.length > 0 && (
                <span className="px-3 py-1 bg-white/20 backdrop-blur-sm text-white rounded-full text-xs font-bold border border-white/30 group-hover:bg-white group-hover:text-orange-600 transition-all">
                  {chatMessages.length}
                </span>
              )}
            </button>
          </div>
        )}

        {/* Floating Chat - Expanded (Futuristic Design) */}
        {!isChatMinimized && (
          <div className="fixed bottom-6 right-6 z-40 w-full max-w-2xl animate-fadeIn">
            <div
              className="rounded-3xl shadow-2xl border backdrop-blur-xl overflow-hidden"
              style={{
                background: "linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 250, 245, 0.95) 100%)",
                borderColor: "rgba(255, 87, 51, 0.2)",
                boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 87, 51, 0.1)",
              }}
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              onDragEnter={(e) => e.preventDefault()}
            >
              {/* Chat Header with Gradient Background */}
              <div 
                className="flex items-center justify-between px-6 py-4 border-b"
                style={{
                  background: "linear-gradient(90deg, rgba(255, 87, 51, 0.08) 0%, rgba(255, 140, 0, 0.05) 100%)",
                  borderColor: "rgba(255, 87, 51, 0.1)",
                }}
              >
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center shadow-lg">
                      <ChatBubbleLeftRightIcon className="h-5 w-5 text-white" />
                    </div>
                    <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white animate-pulse"></div>
                  </div>
                  <div>
                    <span className="text-sm font-bold bg-gradient-to-r from-orange-600 to-orange-500 bg-clip-text text-transparent">
                      AI Legal Assistant
                    </span>
                    <p className="text-xs text-gray-500">Powered by Gemini AI</p>
                  </div>
                </div>
                <button
                  onClick={() => setIsChatMinimized(true)}
                  className="p-2 hover:bg-white/50 rounded-xl transition-all duration-200 group"
                  title="Minimize chat"
                >
                  <MinusIcon className="h-5 w-5 text-gray-400 group-hover:text-orange-600 transition-colors" />
                </button>
              </div>

              {/* Case Selector with Modern Glassmorphism */}
              {(showCaseSelector || !selectedCaseId) && (
                <div 
                  className="mx-6 mt-4 p-4 rounded-2xl border backdrop-blur-sm animate-fadeIn"
                  style={{
                    background: "linear-gradient(135deg, rgba(255, 237, 213, 0.6) 0%, rgba(255, 248, 240, 0.8) 100%)",
                    borderColor: "rgba(255, 87, 51, 0.3)",
                  }}
                >
                  <label className="text-xs font-semibold text-orange-800 block mb-2 flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Select your case
                  </label>
                  <select
                    value={selectedCaseId || ""}
                    onChange={(e) => {
                      setSelectedCaseId(e.target.value);
                      setShowCaseSelector(false);
                    }}
                    className="custom-select w-full px-4 py-3 text-sm border-2 border-orange-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent bg-white/80 backdrop-blur-sm font-medium transition-all"
                    disabled={casesLoading}
                  >
                    <option value="">
                      {casesLoading ? "🔄 Loading cases..." : "📁 Choose a case..."}
                    </option>
                    {cases.map((caseItem) => (
                      <option key={caseItem.case_id} value={caseItem.case_id}>
                        {caseItem.case_name || caseItem.case_id}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Chat Messages with Enhanced Design */}
              {chatMessages.length > 0 && (
                <div className="mx-6 my-4 max-h-64 overflow-y-auto space-y-3 scrollbar-thin scrollbar-thumb-orange-300 scrollbar-track-gray-100">
                  {chatMessages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${
                        message.role === "user"
                          ? "justify-end"
                          : "justify-start"
                      } animate-fadeIn`}
                    >
                      <div
                        className={`max-w-lg px-5 py-3 rounded-2xl text-sm shadow-md transition-all duration-200 hover:shadow-lg ${
                          message.role === "user"
                            ? "bg-gradient-to-r from-orange-500 to-orange-600 text-white"
                            : message.role === "system"
                            ? "bg-red-100 text-red-800 border border-red-200"
                            : "bg-white text-gray-800 border border-gray-200"
                        }`}
                      >
                        <p className="whitespace-pre-wrap break-words leading-relaxed">
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
                      </div>
                    </div>
                  ))}
                  {isProcessing && (
                    <div className="flex justify-start animate-fadeIn">
                      <div className="max-w-md px-5 py-3 rounded-2xl bg-gradient-to-r from-gray-50 to-gray-100 text-gray-800 border border-gray-200 shadow-md">
                        <div className="flex items-center space-x-3">
                          <div className="flex space-x-1">
                            <div className="w-2.5 h-2.5 bg-orange-500 rounded-full animate-bounce"></div>
                            <div
                              className="w-2.5 h-2.5 bg-orange-500 rounded-full animate-bounce"
                              style={{ animationDelay: "0.1s" }}
                            ></div>
                            <div
                              className="w-2.5 h-2.5 bg-orange-500 rounded-full animate-bounce"
                              style={{ animationDelay: "0.2s" }}
                            ></div>
                          </div>
                          <span className="text-xs font-medium text-gray-600">AI is analyzing your request...</span>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>
              )}

              {/* Attachments Display - Futuristic Pills */}
              {attachments.length > 0 && (
                <div className="mx-6 mb-4">
                  <div className="flex flex-wrap gap-2">
                    {attachments.map((file, index) => (
                      <div
                        key={index}
                        className="group flex items-center rounded-full px-4 py-2 text-xs border-2 backdrop-blur-sm transition-all duration-200 hover:scale-105"
                        style={{
                          background: "linear-gradient(135deg, rgba(255, 237, 213, 0.8) 0%, rgba(255, 248, 240, 0.9) 100%)",
                          borderColor: "rgba(255, 87, 51, 0.4)",
                        }}
                      >
                        <div className="w-6 h-6 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center mr-2">
                          <PaperClipIcon className="h-3 w-3 text-white" />
                        </div>
                        <span className="truncate max-w-40 font-medium text-orange-800">
                          {file.name}
                        </span>
                        <button
                          onClick={() => removeAttachment(index)}
                          className="ml-2 w-5 h-5 rounded-full bg-white/50 hover:bg-red-500 flex items-center justify-center transition-all duration-200 group-hover:scale-110"
                        >
                          <XMarkIcon className="h-3 w-3 text-orange-600 group-hover:text-white" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Chat Input - Ultra Modern Design */}
              <div className="px-6 pb-4">
                <div 
                  className="flex items-center space-x-3 p-2 rounded-2xl border-2 transition-all duration-300 bg-white/50 backdrop-blur-sm"
                  style={{
                    borderColor: chatInput.trim() ? "rgba(255, 87, 51, 0.5)" : "rgba(209, 213, 219, 0.5)",
                    boxShadow: chatInput.trim() ? "0 0 0 3px rgba(255, 87, 51, 0.1)" : "none",
                  }}
                >
                  {/* Case Icon */}
                  {selectedCaseId && (
                    <button
                      onClick={() => setShowCaseSelector(!showCaseSelector)}
                      className="p-3 rounded-xl transition-all duration-200 hover:bg-orange-50 group flex-shrink-0"
                      title="Change case"
                    >
                      <svg
                        className="h-5 w-5 text-gray-400 group-hover:text-orange-600 transition-colors"
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
                    </button>
                  )}
                  
                  {/* Input Field */}
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
                    onFocus={() => {
                      if (!selectedCaseId) {
                        setShowCaseSelector(true);
                      }
                    }}
                    placeholder={
                      selectedCaseId
                        ? "✨ Ask anything about your legal case..."
                        : "Select a case first..."
                    }
                    className="flex-1 px-4 py-3 rounded-xl border-0 focus:outline-none bg-transparent text-gray-700 placeholder-gray-400 font-medium"
                    disabled={isProcessing}
                  />
                  
                  {/* Attachment Button */}
                  <label className="cursor-pointer p-3 rounded-xl transition-all duration-200 hover:bg-orange-50 group flex-shrink-0">
                    <div className="relative">
                      <PaperClipIcon className="h-5 w-5 text-gray-400 group-hover:text-orange-600 transition-colors" />
                      {attachments.length > 0 && (
                        <span className="absolute -top-1 -right-1 w-4 h-4 bg-orange-500 text-white text-xs rounded-full flex items-center justify-center font-bold">
                          {attachments.length}
                        </span>
                      )}
                    </div>
                    <input
                      type="file"
                      multiple
                      onChange={handleFileUpload}
                      className="hidden"
                    />
                  </label>
                  
                  {/* Send Button */}
                  <button
                    onClick={handleSendMessage}
                    disabled={
                      isProcessing || !chatInput.trim() || !selectedCaseId
                    }
                    className="px-6 py-3 text-white rounded-xl transition-all duration-200 font-semibold disabled:cursor-not-allowed flex items-center space-x-2 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none flex-shrink-0"
                    style={{ 
                      background: (isProcessing || !chatInput.trim() || !selectedCaseId)
                        ? "#9ca3af"
                        : "linear-gradient(135deg, #ff5733 0%, #ff8c00 100%)",
                      opacity: (isProcessing || !chatInput.trim() || !selectedCaseId) ? 0.6 : 1
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

              {/* Enhanced Status Bar */}
              <div 
                className="px-6 pb-4 pt-2 text-xs text-center border-t"
                style={{ 
                  borderColor: "rgba(255, 87, 51, 0.1)",
                  background: "linear-gradient(to top, rgba(255, 250, 245, 0.5) 0%, transparent 100%)"
                }}
              >
                {selectedCaseId ? (
                  <div className="flex items-center justify-center space-x-2 text-gray-600">
                    <div className="flex items-center space-x-1">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      <span className="font-medium">Active:</span>
                    </div>
                    <span className="font-bold bg-gradient-to-r from-orange-600 to-orange-500 bg-clip-text text-transparent">
                      {cases.find((c) => c.case_id === selectedCaseId)
                        ?.case_name || selectedCaseId}
                    </span>
                    <span className="text-gray-400">•</span>
                    <span className="text-gray-500">Drag & drop files or click 📎</span>
                  </div>
                ) : (
                  <span className="text-gray-500">
                    💡 Select a case above to unlock AI-powered legal assistance
                  </span>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
