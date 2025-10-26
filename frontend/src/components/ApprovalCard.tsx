"use client";

import React, { useState } from "react";
import {
  CheckCircleIcon,
  XCircleIcon,
  EnvelopeIcon,
  CalendarIcon,
  PencilIcon,
} from "@heroicons/react/24/outline";

interface ApprovalCardProps {
  activity: {
    activity_id: string;
    agent_type: string;
    agent_action: string;
    activity_status: string;
    prompt: string;
    action_data?: any;
    created_at: string;
  };
  onApprove: () => void;
  onReject: (reason: string) => void;
}

const ApprovalCard: React.FC<ApprovalCardProps> = ({
  activity,
  onApprove,
  onReject,
}) => {
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectReason, setRejectReason] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  const handleApprove = async () => {
    setIsProcessing(true);
    await onApprove();
    setIsProcessing(false);
  };

  const handleReject = async () => {
    if (!rejectReason.trim()) {
      alert("Please provide a reason for rejection");
      return;
    }
    setIsProcessing(true);
    await onReject(rejectReason);
    setShowRejectModal(false);
    setRejectReason("");
    setIsProcessing(false);
  };

  // Render email draft
  if (activity.agent_action === "draft_email" && activity.action_data) {
    const { draft, to, subject } = activity.action_data;

    return (
      <div className="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-6 my-4">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <EnvelopeIcon className="h-6 w-6 text-blue-600" />
          </div>
          <div className="ml-4 flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              📧 Email Draft Ready for Approval
            </h3>

            <div className="bg-white rounded-lg p-4 mb-4 border border-blue-200">
              <div className="space-y-2 mb-4">
                <div className="flex items-center text-sm">
                  <span className="font-medium text-gray-700 w-20">To:</span>
                  <span className="text-gray-900">{to}</span>
                </div>
                <div className="flex items-center text-sm">
                  <span className="font-medium text-gray-700 w-20">
                    Subject:
                  </span>
                  <span className="text-gray-900">{subject}</span>
                </div>
              </div>

              <div className="border-t border-gray-200 pt-4">
                <pre className="whitespace-pre-wrap text-sm text-gray-800 font-sans">
                  {draft}
                </pre>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={handleApprove}
                disabled={isProcessing}
                className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <CheckCircleIcon className="h-5 w-5 mr-2" />
                {isProcessing ? "Approving..." : "Approve & Send"}
              </button>

              <button
                onClick={() => setShowRejectModal(true)}
                disabled={isProcessing}
                className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <XCircleIcon className="h-5 w-5 mr-2" />
                Reject
              </button>

              <button
                disabled={isProcessing}
                className="flex items-center px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <PencilIcon className="h-5 w-5 mr-2" />
                Edit
              </button>
            </div>

            <p className="text-xs text-gray-500 mt-3">
              Created: {new Date(activity.created_at).toLocaleString()}
            </p>
          </div>
        </div>

        {/* Reject Modal */}
        {showRejectModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Reject Email Draft
              </h3>
              <textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="Please provide a reason for rejection..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 mb-4"
                rows={4}
              />
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowRejectModal(false);
                    setRejectReason("");
                  }}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                >
                  Cancel
                </button>
                <button
                  onClick={handleReject}
                  disabled={isProcessing}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                >
                  {isProcessing ? "Rejecting..." : "Confirm Rejection"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Render appointment scheduling
  if (
    activity.agent_action === "schedule_appointment" &&
    activity.action_data
  ) {
    const { appointment_type, date, time, duration, attendees, notes } =
      activity.action_data;

    return (
      <div className="bg-purple-50 border-l-4 border-purple-500 rounded-lg p-6 my-4">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <CalendarIcon className="h-6 w-6 text-purple-600" />
          </div>
          <div className="ml-4 flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              📅 Appointment Request
            </h3>

            <div className="bg-white rounded-lg p-4 mb-4 border border-purple-200">
              <div className="space-y-3">
                <div>
                  <span className="font-medium text-gray-700">Type:</span>
                  <span className="ml-2 text-gray-900">{appointment_type}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Date:</span>
                  <span className="ml-2 text-gray-900">
                    {new Date(date).toLocaleDateString("en-US", {
                      weekday: "long",
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    })}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Time:</span>
                  <span className="ml-2 text-gray-900">
                    {time} ({duration})
                  </span>
                </div>
                {attendees && attendees.length > 0 && (
                  <div>
                    <span className="font-medium text-gray-700">
                      Attendees:
                    </span>
                    <ul className="ml-6 mt-1 list-disc">
                      {attendees.map((attendee: string, index: number) => (
                        <li key={index} className="text-gray-900">
                          {attendee}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {notes && (
                  <div>
                    <span className="font-medium text-gray-700">Notes:</span>
                    <p className="ml-2 text-gray-900">{notes}</p>
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={handleApprove}
                disabled={isProcessing}
                className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <CheckCircleIcon className="h-5 w-5 mr-2" />
                {isProcessing ? "Approving..." : "Approve & Schedule"}
              </button>

              <button
                onClick={() => setShowRejectModal(true)}
                disabled={isProcessing}
                className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <XCircleIcon className="h-5 w-5 mr-2" />
                Reject
              </button>

              <button
                disabled={isProcessing}
                className="flex items-center px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <PencilIcon className="h-5 w-5 mr-2" />
                Edit
              </button>
            </div>

            <p className="text-xs text-gray-500 mt-3">
              Created: {new Date(activity.created_at).toLocaleString()}
            </p>
          </div>
        </div>

        {/* Reject Modal */}
        {showRejectModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Reject Appointment
              </h3>
              <textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="Please provide a reason for rejection..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 mb-4"
                rows={4}
              />
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowRejectModal(false);
                    setRejectReason("");
                  }}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                >
                  Cancel
                </button>
                <button
                  onClick={handleReject}
                  disabled={isProcessing}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                >
                  {isProcessing ? "Rejecting..." : "Confirm Rejection"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Fallback for unknown action types
  return null;
};

export default ApprovalCard;
