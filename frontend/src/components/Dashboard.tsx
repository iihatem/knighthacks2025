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
      className="min-h-screen"
      style={{ backgroundColor: "var(--color-bg-primary)" }}
    >
      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out flex flex-col ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div
          className="flex items-center justify-between h-16 px-4 border-b"
          style={{ borderColor: "var(--color-gray-light)" }}
        >
          <div className="flex items-center">
            <div className="w-18 h-18 flex items-center justify-center">
              <img
                src="/briefly_logo.svg"
                alt="Briefly Logo"
                className="w-full h-full"
              />
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        <div className="flex flex-col flex-1">
          <nav className="mt-5 px-2 flex-1">
            <div className="space-y-2">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`${
                      item.current ? "border-r-2" : "hover:bg-gray-50"
                    } group flex items-center px-4 py-4 text-base font-medium rounded-lg transition-all duration-200`}
                    style={{
                      backgroundColor: item.current
                        ? "rgba(255, 87, 51, 0.1)"
                        : "transparent",
                      color: item.current
                        ? "var(--color-accent-orange)"
                        : "var(--color-text-secondary)",
                      borderColor: item.current
                        ? "var(--color-accent-orange)"
                        : "transparent",
                    }}
                  >
                    <Icon
                      className="mr-4 h-6 w-6"
                      style={{
                        color: item.current
                          ? "var(--color-accent-orange)"
                          : "var(--color-gray-medium)",
                      }}
                    />
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </nav>

          {/* Settings Button at Bottom */}
          <div className="px-2 pb-4">
            <Link
              href="/settings"
              className={`${
                pathname === "/settings" ? "border-r-2" : "hover:bg-gray-50"
              } group flex items-center px-4 py-4 text-base font-medium rounded-lg transition-all duration-200`}
              style={{
                backgroundColor:
                  pathname === "/settings"
                    ? "rgba(255, 87, 51, 0.1)"
                    : "transparent",
                color:
                  pathname === "/settings"
                    ? "var(--color-accent-orange)"
                    : "var(--color-text-secondary)",
                borderColor:
                  pathname === "/settings"
                    ? "var(--color-accent-orange)"
                    : "transparent",
              }}
            >
              <CogIcon
                className="mr-4 h-6 w-6"
                style={{
                  color:
                    pathname === "/settings"
                      ? "var(--color-accent-orange)"
                      : "var(--color-gray-medium)",
                }}
              />
              Settings
            </Link>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div
        className={`transition-all duration-300 ease-in-out ${
          sidebarOpen ? "ml-64" : "ml-0"
        }`}
      >
        {/* Header */}
        <header
          className="bg-white shadow-sm border-b"
          style={{
            backgroundColor: "var(--color-bg-card)",
            borderColor: "var(--color-gray-light)",
          }}
        >
          <div className="flex items-center justify-between h-16 px-6">
            <div className="flex items-center space-x-8">
              {!sidebarOpen && (
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100"
                >
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
                      d="M4 6h16M4 12h16M4 18h16"
                    />
                  </svg>
                </button>
              )}

              {/* Navigation Menu */}
              <nav className="hidden md:flex space-x-8">
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
                <Link
                  href="/calendar"
                  className="font-medium pb-1"
                  style={{
                    color:
                      pathname === "/calendar"
                        ? "var(--color-text-primary)"
                        : "var(--color-text-secondary)",
                    borderBottom:
                      pathname === "/calendar"
                        ? "2px solid var(--color-accent-orange)"
                        : "none",
                  }}
                >
                  Calendar
                </Link>
                <Link
                  href="/analytics"
                  className="font-medium pb-1"
                  style={{
                    color:
                      pathname === "/analytics"
                        ? "var(--color-text-primary)"
                        : "var(--color-text-secondary)",
                    borderBottom:
                      pathname === "/analytics"
                        ? "2px solid var(--color-accent-orange)"
                        : "none",
                  }}
                >
                  Analytics
                </Link>
              </nav>
            </div>

            {/* Search Bar */}
            <div className="flex-1 max-w-md mx-8">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Enter your search request..."
                  className="w-full px-4 py-2 rounded-full pl-10 pr-4 focus:outline-none"
                  style={{
                    backgroundColor: "var(--color-gray-light)",
                    color: "var(--color-text-primary)",
                  }}
                />
                <svg
                  className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  style={{ color: "var(--color-gray-medium)" }}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full">
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
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              </button>
              <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full">
                <BellIcon className="h-5 w-5" />
              </button>
              <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full">
                <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                  <UserCircleIcon className="h-6 w-6" />
                </div>
              </button>
            </div>
          </div>
        </header>

        {/* Main content area */}
        <main className="flex-1 p-6">{children}</main>

        {/* Floating Chat - Minimized Button */}
        {isChatMinimized && (
          <div className="fixed bottom-8 left-1/2 transform -translate-x-1/2 z-40">
            <button
              onClick={() => setIsChatMinimized(false)}
              className="px-8 py-4 bg-orange-500 text-white rounded-full shadow-2xl hover:bg-orange-600 transition-all duration-200 flex items-center space-x-3 font-medium"
            >
              <ChatBubbleLeftRightIcon className="h-6 w-6" />
              <span>
                {selectedCaseId
                  ? `Chat about ${
                      cases.find((c) => c.case_id === selectedCaseId)
                        ?.case_name || "case"
                    }`
                  : "Open AI Assistant"}
              </span>
              {chatMessages.length > 0 && (
                <span className="px-2 py-1 bg-white text-orange-600 rounded-full text-xs font-bold">
                  {chatMessages.length}
                </span>
              )}
            </button>
          </div>
        )}

        {/* Floating Chat - Expanded (Centered, Skinny, Wide with Round Edges + AI Functionality) */}
        {!isChatMinimized && (
          <div className="fixed bottom-8 left-1/2 transform -translate-x-1/2 z-40 w-full max-w-4xl px-4">
            <div
              className="rounded-3xl shadow-2xl border p-6"
              style={{
                backgroundColor: "var(--color-bg-card)",
                borderColor: "var(--color-gray-light)",
              }}
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              onDragEnter={(e) => e.preventDefault()}
            >
              {/* Chat Header with Minimize Button */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <ChatBubbleLeftRightIcon className="h-5 w-5 text-orange-600" />
                  <span className="text-sm font-medium text-gray-700">
                    AI Legal Assistant
                  </span>
                </div>
                <button
                  onClick={() => setIsChatMinimized(true)}
                  className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                  title="Minimize chat"
                >
                  <MinusIcon className="h-5 w-5 text-gray-500" />
                </button>
              </div>

              {/* Case Selector (shown when clicked or when no case selected) */}
              {(showCaseSelector || !selectedCaseId) && (
                <div className="mb-4 p-3 bg-orange-50 rounded-2xl border border-orange-200">
                  <label className="text-xs font-medium text-orange-800 block mb-2">
                    Select a case to chat about:
                  </label>
                  <select
                    value={selectedCaseId || ""}
                    onChange={(e) => {
                      setSelectedCaseId(e.target.value);
                      setShowCaseSelector(false);
                    }}
                    className="w-full px-4 py-2 text-sm border border-orange-300 rounded-full focus:outline-none focus:ring-2 focus:ring-orange-500"
                    disabled={casesLoading}
                  >
                    <option value="">
                      {casesLoading ? "Loading cases..." : "Choose a case..."}
                    </option>
                    {cases.map((caseItem) => (
                      <option key={caseItem.case_id} value={caseItem.case_id}>
                        {caseItem.case_name || caseItem.case_id}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Chat Messages (if any) */}
              {chatMessages.length > 0 && (
                <div className="mb-4 max-h-48 overflow-y-auto space-y-2">
                  {chatMessages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${
                        message.role === "user"
                          ? "justify-end"
                          : "justify-start"
                      }`}
                    >
                      <div
                        className={`max-w-md px-4 py-2 rounded-2xl text-sm ${
                          message.role === "user"
                            ? "bg-orange-500 text-white"
                            : message.role === "system"
                            ? "bg-red-100 text-red-800"
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
                      </div>
                    </div>
                  ))}
                  {isProcessing && (
                    <div className="flex justify-start">
                      <div className="max-w-md px-4 py-2 rounded-2xl bg-gray-100 text-gray-800">
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
                          <span className="text-xs">AI is thinking...</span>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>
              )}

              {/* Attachments display */}
              {attachments.length > 0 && (
                <div className="mb-4">
                  <div className="flex flex-wrap gap-2">
                    {attachments.map((file, index) => (
                      <div
                        key={index}
                        className="flex items-center rounded-full px-3 py-1 text-xs border"
                        style={{
                          backgroundColor: "rgba(255, 87, 51, 0.1)",
                          borderColor: "var(--color-accent-orange)",
                        }}
                      >
                        <PaperClipIcon
                          className="h-3 w-3 mr-2"
                          style={{ color: "var(--color-accent-orange)" }}
                        />
                        <span
                          className="truncate max-w-32"
                          style={{ color: "var(--color-accent-orange)" }}
                        >
                          {file.name}
                        </span>
                        <button
                          onClick={() => removeAttachment(index)}
                          className="ml-2"
                          style={{ color: "var(--color-accent-orange)" }}
                        >
                          <XMarkIcon className="h-3 w-3" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Chat input */}
              <div className="flex items-center space-x-4">
                <div className="flex-1">
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
                        ? "Ask me anything about your legal case..."
                        : "Select a case first..."
                    }
                    className="w-full px-6 py-4 rounded-full border-0 focus:outline-none"
                    style={{
                      backgroundColor: "var(--color-gray-light)",
                      color: "var(--color-text-primary)",
                    }}
                    disabled={isProcessing}
                  />
                </div>
                <div className="flex items-center space-x-2">
                  {selectedCaseId && (
                    <button
                      onClick={() => setShowCaseSelector(!showCaseSelector)}
                      className="p-3 rounded-full transition-all duration-200 hover:bg-gray-200"
                      style={{ color: "var(--color-gray-medium)" }}
                      title="Change case"
                    >
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
                          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        />
                      </svg>
                    </button>
                  )}
                  <label
                    className="cursor-pointer p-3 rounded-full transition-all duration-200 hover:bg-gray-200"
                    style={{ color: "var(--color-gray-medium)" }}
                  >
                    <PaperClipIcon className="h-5 w-5" />
                    <input
                      type="file"
                      multiple
                      onChange={handleFileUpload}
                      className="hidden"
                    />
                  </label>
                  <button
                    onClick={handleSendMessage}
                    disabled={
                      isProcessing || !chatInput.trim() || !selectedCaseId
                    }
                    className="px-6 py-4 text-white rounded-full transition-all duration-200 font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                    style={{ backgroundColor: "var(--color-accent-orange)" }}
                  >
                    {isProcessing ? (
                      <span>Sending...</span>
                    ) : (
                      <>
                        <span>Send</span>
                        <PaperAirplaneIcon className="h-5 w-5" />
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Hint text */}
              <div
                className="mt-3 text-xs text-center"
                style={{ color: "var(--color-gray-medium)" }}
              >
                {selectedCaseId ? (
                  <>
                    Chatting about:{" "}
                    <span className="font-medium text-orange-600">
                      {cases.find((c) => c.case_id === selectedCaseId)
                        ?.case_name || selectedCaseId}
                    </span>{" "}
                    • Drag and drop files here or click the attachment icon
                  </>
                ) : (
                  "Select a case above to start chatting with your AI assistant"
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
