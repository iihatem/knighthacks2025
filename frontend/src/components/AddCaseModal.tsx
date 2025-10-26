"use client";

import React, { useState } from "react";
import {
  XMarkIcon,
  PaperClipIcon,
  DocumentIcon,
} from "@heroicons/react/24/outline";
import { useCreateCase } from "@/hooks/useCases";
import { useRouter } from "next/navigation";

interface AddCaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  redirectToCase?: boolean; // Optional: control whether to redirect
}

interface CaseFormData {
  caseName: string;
  clientName: string;
  clientPhone: string;
  clientEmail: string;
  address: string;
}

const AddCaseModal: React.FC<AddCaseModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  redirectToCase = true, // Default to true
}) => {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<CaseFormData>({
    caseName: "",
    clientName: "",
    clientPhone: "",
    clientEmail: "",
    address: "",
  });
  const [files, setFiles] = useState<File[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [createdCaseId, setCreatedCaseId] = useState<string | null>(null);
  const [createdCaseNumber, setCreatedCaseNumber] = useState<string | null>(
    null
  );

  const {
    create,
    loading: createLoading,
    error: createError,
  } = useCreateCase();

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    setFiles((prev) => [...prev, ...selectedFiles]);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const droppedFiles = Array.from(e.dataTransfer.files);
    setFiles((prev) => [...prev, ...droppedFiles]);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleNext = () => {
    if (currentStep === 1) {
      // Validate form data
      if (
        !formData.caseName ||
        !formData.clientName ||
        !formData.clientPhone ||
        !formData.clientEmail
      ) {
        alert("Please fill in all required fields");
        return;
      }
    }
    setCurrentStep((prev) => prev + 1);
  };

  const handleBack = () => {
    setCurrentStep((prev) => prev - 1);
  };

  const handleSubmit = async () => {
    setIsCreating(true);

    try {
      // Call the actual API
      const response = await create({
        case_name: formData.caseName,
        client_name: formData.clientName,
        client_phone: formData.clientPhone || undefined,
        client_email: formData.clientEmail || undefined,
        files: files.length > 0 ? files : undefined,
      });

      // Store the created case info
      setCreatedCaseId(response.case_id);
      setCreatedCaseNumber(response.case_number);

      // Wait a bit to show success animation
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Reset form
      setFormData({
        caseName: "",
        clientName: "",
        clientPhone: "",
        clientEmail: "",
        address: "",
      });
      setFiles([]);
      setCurrentStep(1);
      setIsCreating(false);

      // Call onSuccess callback if provided
      if (onSuccess) {
        onSuccess();
      }

      // Close modal
      onClose();

      // Redirect to the case page if enabled
      if (redirectToCase && response.case_id) {
        // Convert case_id to slug format (remove "case-" prefix for cleaner URLs)
        const caseSlug = response.case_id;
        router.push(`/case/${caseSlug}`);
      }
    } catch (error) {
      console.error("Error creating case:", error);
      setIsCreating(false);
      alert(createError || "Failed to create case. Please try again.");
    }
  };

  const handleClose = () => {
    if (!isCreating) {
      setFormData({
        caseName: "",
        clientName: "",
        clientPhone: "",
        clientEmail: "",
        address: "",
      });
      setFiles([]);
      setCurrentStep(1);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 flex items-center justify-center z-50 p-4"
      style={{ backgroundColor: "rgba(0, 0, 0, 0.2)" }}
    >
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800">
            {currentStep === 1 && "Add New Case"}
            {currentStep === 2 && "Upload Case Files"}
            {currentStep === 3 && "Creating Case"}
          </h2>
          <button
            onClick={handleClose}
            disabled={isCreating}
            className="p-2 text-gray-400 hover:text-gray-600 disabled:opacity-50"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="px-6 py-4 bg-gray-50">
          <div className="flex items-center space-x-2">
            {[1, 2, 3].map((step) => (
              <div key={step} className="flex items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    step <= currentStep
                      ? "bg-orange-500 text-white"
                      : "bg-gray-200 text-gray-500"
                  }`}
                >
                  {step}
                </div>
                {step < 3 && (
                  <div
                    className={`w-12 h-1 mx-2 ${
                      step < currentStep ? "bg-orange-500" : "bg-gray-200"
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {currentStep === 1 && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Case Name *
                </label>
                <input
                  type="text"
                  name="caseName"
                  value={formData.caseName}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  placeholder="Enter case name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Client Name *
                </label>
                <input
                  type="text"
                  name="clientName"
                  value={formData.clientName}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  placeholder="Enter client name"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number *
                  </label>
                  <input
                    type="tel"
                    name="clientPhone"
                    value={formData.clientPhone}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    placeholder="Enter phone number"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address *
                  </label>
                  <input
                    type="email"
                    name="clientEmail"
                    value={formData.clientEmail}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    placeholder="Enter email address"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Address (Optional)
                </label>
                <textarea
                  name="address"
                  value={formData.address}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  placeholder="Enter client address"
                />
              </div>
            </div>
          )}

          {currentStep === 2 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-800 mb-4">
                  Upload Case Files
                </h3>
                <p className="text-sm text-gray-600 mb-6">
                  Upload documents, photos, or other files related to this case.
                </p>
              </div>

              {/* File Upload Area */}
              <div
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  isDragOver
                    ? "border-orange-500 bg-orange-50"
                    : "border-gray-300 hover:border-gray-400"
                }`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
              >
                <DocumentIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-lg font-medium text-gray-700 mb-2">
                  Drop files here or click to browse
                </p>
                <p className="text-sm text-gray-500 mb-4">
                  Supports PDF, DOC, DOCX, JPG, PNG, and other common formats
                </p>
                <label className="inline-flex items-center px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 cursor-pointer transition-colors">
                  <PaperClipIcon className="h-4 w-4 mr-2" />
                  Select Files
                  <input
                    type="file"
                    multiple
                    onChange={handleFileUpload}
                    className="hidden"
                    accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.txt,.eml"
                  />
                </label>
              </div>

              {/* File List */}
              {files.length > 0 && (
                <div className="space-y-3">
                  <h4 className="font-medium text-gray-800">
                    Selected Files ({files.length})
                  </h4>
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {files.map((file, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div className="flex items-center">
                          <DocumentIcon className="h-5 w-5 text-gray-400 mr-3" />
                          <div>
                            <p className="text-sm font-medium text-gray-800">
                              {file.name}
                            </p>
                            <p className="text-xs text-gray-500">
                              {(file.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                          </div>
                        </div>
                        <button
                          onClick={() => removeFile(index)}
                          className="p-1 text-gray-400 hover:text-red-500"
                        >
                          <XMarkIcon className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {currentStep === 3 && (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-2 border-orange-500 mb-6"></div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">
                Creating Your Case
              </h3>
              <p className="text-gray-600 mb-6">
                Please wait while we process your case information and upload
                your files...
              </p>
              <div className="space-y-2 text-sm text-gray-500">
                <p>✓ Validating case information</p>
                <p>✓ Processing uploaded files</p>
                <p>✓ Creating case record</p>
                <p className="text-orange-600">⏳ Finalizing setup...</p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        {currentStep < 3 && (
          <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
            <button
              onClick={currentStep === 1 ? handleClose : handleBack}
              className="px-6 py-2 text-gray-600 hover:text-gray-800 font-medium"
            >
              {currentStep === 1 ? "Cancel" : "Back"}
            </button>
            <button
              onClick={currentStep === 2 ? handleSubmit : handleNext}
              className="px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 font-medium transition-colors"
            >
              {currentStep === 2 ? "Create Case" : "Next"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AddCaseModal;
