# Frontend API Integration Guide

## 📁 File Structure

```
frontend/src/
├── types/
│   └── case.ts              # TypeScript type definitions for API responses
├── lib/
│   └── api.ts               # API service layer with all endpoint functions
├── hooks/
│   ├── useCases.ts          # React hooks for case management
│   └── useRAG.ts            # React hooks for RAG search and AI agents
└── components/
    └── AddCaseModal.tsx     # Updated to use real API
```

## 🔧 Setup

### 1. Environment Variables

The frontend needs to know where the backend API is running. By default, it uses `http://localhost:5001`.

To customize, you can set the environment variable in your deployment or locally:

```bash
# In your terminal or .env.local file (not tracked by git)
NEXT_PUBLIC_API_URL=http://localhost:5001
```

### 2. Backend Must Be Running

Make sure your Flask backend is running on port 5001:

```bash
cd backend
python app.py
```

## 📚 API Service Layer (`src/lib/api.ts`)

All backend API calls are centralized in this file. Import and use these functions:

### Case Management

```typescript
import { createCase, addCaseFiles, listCases, viewCaseData } from "@/lib/api";

// Create a new case
const response = await createCase({
  case_name: "Smith vs ABC Insurance",
  client_name: "John Smith",
  client_phone: "(555) 123-4567",
  client_email: "john@email.com",
  files: [file1, file2], // Optional
});

// Add files to existing case
await addCaseFiles({
  case_id: "case-abc-123...",
  files: [file1, file2],
});

// List all cases
const { cases, total_cases } = await listCases();

// View case data
const caseData = await viewCaseData("case-abc-123...");
```

### RAG Search

```typescript
import { ragSearch } from "@/lib/api";

const results = await ragSearch({
  case_id: "case-abc-123...",
  query: "What injuries did the plaintiff suffer?",
  top_k: 5, // Optional, defaults to 5
});
```

### AI Agents

```typescript
import { processWithAgent } from "@/lib/api";

const result = await processWithAgent({
  case_id: "case-abc-123...",
  query: "Draft an email to the client about settlement",
});
```

## 🪝 React Hooks

Pre-built hooks for common operations with built-in loading/error states.

### `useCases()` - Fetch all cases

```typescript
import { useCases } from "@/hooks/useCases";

function MyComponent() {
  const { cases, loading, error, refetch } = useCases();

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {cases.map((case) => (
        <div key={case.case_id}>
          {case.case_number} - {case.case_name}
        </div>
      ))}
      <button onClick={refetch}>Refresh</button>
    </div>
  );
}
```

### `useCaseData(caseId)` - Fetch single case data

```typescript
import { useCaseData } from "@/hooks/useCases";

function CaseDetails({ caseId }: { caseId: string }) {
  const { caseData, loading, error, refetch } = useCaseData(caseId);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>{caseData?.case_id}</h1>
      <p>Total chunks: {caseData?.total_chunks}</p>
    </div>
  );
}
```

### `useCreateCase()` - Create a new case

```typescript
import { useCreateCase } from "@/hooks/useCases";

function CreateCaseForm() {
  const { create, loading, error, success } = useCreateCase();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await create({
        case_name: "New Case",
        client_name: "Client Name",
        files: selectedFiles,
      });
      console.log("Created:", response.case_id);
    } catch (err) {
      console.error("Failed:", err);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* form fields */}
      <button disabled={loading}>
        {loading ? "Creating..." : "Create Case"}
      </button>
      {error && <div>Error: {error}</div>}
      {success && <div>Case created successfully!</div>}
    </form>
  );
}
```

### `useRAGSearch()` - Search case knowledge base

```typescript
import { useRAGSearch } from "@/hooks/useRAG";

function SearchComponent({ caseId }: { caseId: string }) {
  const { search, results, loading, error } = useRAGSearch();

  const handleSearch = async (query: string) => {
    await search({ case_id: caseId, query, top_k: 5 });
  };

  return (
    <div>
      <input
        type="text"
        onKeyPress={(e) => {
          if (e.key === "Enter") handleSearch(e.currentTarget.value);
        }}
      />
      {loading && <div>Searching...</div>}
      {results?.results.map((result, i) => (
        <div key={i}>
          <p>{result.text_chunk}</p>
          <small>Score: {result.similarity_score}</small>
        </div>
      ))}
    </div>
  );
}
```

### `useAgentProcess()` - Process with AI agent

```typescript
import { useAgentProcess } from "@/hooks/useRAG";

function AgentComponent({ caseId }: { caseId: string }) {
  const { process, result, loading, error } = useAgentProcess();

  const handleProcess = async (query: string) => {
    await process({ case_id: caseId, query });
  };

  return (
    <div>
      <button onClick={() => handleProcess("Draft email to client")}>
        Draft Email
      </button>
      {loading && <div>Processing...</div>}
      {result && (
        <div>
          <h3>Agent: {result.result.delegated_to}</h3>
          <pre>{JSON.stringify(result.result.proposed_actions, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
```

## 📊 TypeScript Types

All API request/response types are defined in `src/types/case.ts`:

```typescript
import type {
  Case,
  CreateCaseRequest,
  CreateCaseResponse,
  RAGSearchRequest,
  RAGSearchResponse,
  // ... and more
} from "@/types/case";
```

## 🎯 Example: Complete Integration

Here's how the `AddCaseModal` component uses the API:

```typescript
import { useCreateCase } from "@/hooks/useCases";

function AddCaseModal({ isOpen, onClose, onSuccess }) {
  const { create, loading, error } = useCreateCase();

  const handleSubmit = async () => {
    try {
      const response = await create({
        case_name: formData.caseName,
        client_name: formData.clientName,
        client_phone: formData.clientPhone,
        client_email: formData.clientEmail,
        files: selectedFiles,
      });

      console.log("Created case:", response.case_id);

      // Notify parent to refresh
      if (onSuccess) onSuccess();

      // Close modal
      onClose();
    } catch (err) {
      alert("Failed to create case");
    }
  };

  return (
    <div>
      {/* form fields */}
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? "Creating..." : "Create Case"}
      </button>
      {error && <div>Error: {error}</div>}
    </div>
  );
}
```

## 🔍 Utility Functions

The API module also exports utility functions:

```typescript
import {
  formatCaseNumber,
  formatFileCount,
  getSimilarityInterpretation,
  caseHasFiles,
} from "@/lib/api";

// Format case number for display
const formatted = formatCaseNumber("MM-2025-00001"); // "MM-2025-00001"

// Format file count
const fileText = formatFileCount(5); // "5 documents"
const noFiles = formatFileCount(1); // "No files"

// Get similarity score interpretation
const { label, color } = getSimilarityInterpretation(0.95);
// { label: "Extremely relevant", color: "text-green-600" }

// Check if case has files
const hasFiles = caseHasFiles(5, "https://..."); // true
const noFiles = caseHasFiles(1, "metadata-only"); // false
```

## 🚨 Error Handling

All API functions throw errors that can be caught:

```typescript
try {
  const response = await createCase(data);
  // Success
} catch (error) {
  console.error("API Error:", error.message);
  // Handle error (show toast, alert, etc.)
}
```

The hooks automatically capture errors in their `error` state:

```typescript
const { cases, error } = useCases();

if (error) {
  return <div>Error: {error}</div>;
}
```

## 🔄 Refreshing Data

After creating/updating cases, refresh the list:

```typescript
const { cases, refetch } = useCases();

// After creating a case
await createCase(data);
refetch(); // Refresh the list
```

## 📝 Notes

- All API calls are asynchronous (`async/await`)
- File uploads use `FormData` (handled automatically)
- JSON requests use `Content-Type: application/json`
- Errors are thrown and should be caught with try/catch
- The backend must be running on port 5001 (or custom `NEXT_PUBLIC_API_URL`)

## 🎉 Ready to Use!

The API integration is complete and ready to use throughout your frontend. Just import the hooks or API functions and start building!
