"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
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
} from "@heroicons/react/24/outline";

interface DashboardProps {
  children?: React.ReactNode;
}

const Dashboard: React.FC<DashboardProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [attachments, setAttachments] = useState<File[]>([]);
  const pathname = usePathname();

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
    const files = Array.from(event.dataTransfer.files);
    setAttachments((prev) => [...prev, ...files]);
  };

  const removeAttachment = (index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
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

        {/* Floating Chat - Centered, Skinny, Wide with Round Edges */}
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
                  placeholder="Ask me anything about your legal case..."
                  className="w-full px-6 py-4 rounded-full border-0 focus:outline-none"
                  style={{
                    backgroundColor: "var(--color-gray-light)",
                    color: "var(--color-text-primary)",
                  }}
                />
              </div>
              <div className="flex items-center space-x-2">
                <label
                  className="cursor-pointer p-3 rounded-full transition-all duration-200"
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
                  className="px-6 py-4 text-white rounded-full transition-all duration-200 font-medium"
                  style={{ backgroundColor: "var(--color-accent-orange)" }}
                >
                  Send
                </button>
              </div>
            </div>

            {/* Drag and drop hint */}
            <div
              className="mt-3 text-xs text-center"
              style={{ color: "var(--color-gray-medium)" }}
            >
              Drag and drop files here or click the attachment icon
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
