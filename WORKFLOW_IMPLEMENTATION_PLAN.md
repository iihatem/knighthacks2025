# 🎯 AI Orchestrator Workflow Implementation Plan

## Overview

This document maps your desired AI Orchestrator workflow to the existing backend API capabilities and outlines the implementation strategy for the chat-based interface.

---

## ✅ Current API Capabilities vs. Desired Workflow

### **Your Desired Workflow:**

```
Multi-Source Input → AI Orchestrator → Route to Specialist → Human Approval → Execute
```

### **What the API Already Supports:**

| Workflow Step          | API Support          | Endpoint                                  | Status                                                   |
| ---------------------- | -------------------- | ----------------------------------------- | -------------------------------------------------------- |
| **Multi-Source Input** | ✅ Fully Supported   | `/api/create-case`, `/api/add-case-files` | Files (PDF, images, text, emails) processed and embedded |
| **AI Orchestrator**    | ✅ Fully Implemented | `/api/agent/process`                      | Gemini-powered routing with session management           |
| **Specialist Routing** | ✅ Working           | `/api/agent/process`                      | Routes to correct agent based on action type             |
| **Human Approval**     | ✅ Implemented       | `/api/activities/*`                       | Activity logging for approval-needed actions             |
| **Execute**            | ⚠️ Partial           | N/A                                       | Returns drafts, no actual execution (email/scheduling)   |

---

## 🤖 AI Specialist Team Mapping

### **Your Desired Specialists vs. Current Implementation:**

| Your Specialist               | Current Agent                        | Action Type                              | Status                  | Notes                                    |
| ----------------------------- | ------------------------------------ | ---------------------------------------- | ----------------------- | ---------------------------------------- |
| **Records Wrangler**          | ❌ Not Yet                           | `request_records`                        | 🔨 Needs Implementation | Can build on RAG search                  |
| **Client Communication Guru** | ✅ `ClientCommunicationGuru`         | `draft_email`                            | ✅ Working              | Drafts empathetic client messages        |
| **Legal Researcher**          | ⚠️ `LegalResearcher` (Placeholder)   | `research_internal`, `research_external` | 🔨 Needs Enhancement    | RAG search works, needs web search       |
| **Voice Bot Scheduler**       | ⚠️ `VoiceBotScheduler` (Placeholder) | `schedule_appointment`                   | 🔨 Needs Implementation | Activity logging works, no calendar API  |
| **Evidence Sorter**           | ❌ Not Yet                           | `organize_evidence`                      | 🔨 Needs Implementation | File processing exists, needs Salesforce |

---

## 📊 How the Chat Interface Should Work

### **Current Flow (What's Already Built):**

```mermaid
User Message
    ↓
/api/agent/process
    ↓
Step 1: Session Detection
    - Checks for existing session (last 30 min)
    - Creates new session if needed
    ↓
Step 2: Context Retrieval
    - Gets last 5 messages from session
    ↓
Step 3: Gemini Analysis
    - Determines: is_continuation, topic, action_type, requires_approval
    ↓
Step 4: Agent Routing
    ├─ research_internal → RAG Search (no approval)
    ├─ research_external → Web Search (no approval)
    ├─ general_query → Gemini Analysis (no approval)
    ├─ draft_email → ClientCommunicationGuru (requires approval ✅)
    └─ schedule_appointment → VoiceBotScheduler (requires approval ✅)
    ↓
Step 5: Activity Logging (Conditional)
    - ONLY logs if requires_approval = true
    - Creates entry in agent_activities table
    ↓
Step 6: Response
    - Stores message in session_messages
    - Returns structured response to frontend
```

### **What Gets Displayed in Chat:**

#### **Scenario 1: Research Query (No Approval Needed)**

```json
// User: "What injuries did the client suffer?"

// API Response:
{
  "status": "success",
  "action_type": "research_internal",
  "requires_approval": false,
  "result": "Based on the medical records, the client suffered...",
  "activity_logged": false
}

// Frontend Display:
┌─────────────────────────────────────────┐
│ 👤 You: What injuries did the client   │
│         suffer?                         │
├─────────────────────────────────────────┤
│ 🤖 AI: Based on the medical records,   │
│        the client suffered fractured    │
│        ribs and a concussion...         │
│                                         │
│        📄 Sources:                      │
│        • medical_report.pdf             │
│        • police_report.pdf              │
└─────────────────────────────────────────┘
```

#### **Scenario 2: Email Draft (Approval Required)**

```json
// User: "Draft an email to John Smith about his settlement offer"

// API Response:
{
  "status": "success",
  "action_type": "draft_email",
  "requires_approval": true,
  "result": {
    "draft": "Dear John,\n\nI hope this email finds you well...",
    "to": "john@email.com",
    "subject": "Important Update on Your Settlement Offer"
  },
  "activity_logged": true,
  "activity_id": "act-20251026-xyz"
}

// Frontend Display:
┌─────────────────────────────────────────┐
│ 👤 You: Draft an email to John Smith   │
│         about his settlement offer      │
├─────────────────────────────────────────┤
│ 🤖 AI: I've drafted an email for your  │
│        approval:                        │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 📧 Email Draft                      │ │
│ │ ─────────────────────────────────── │ │
│ │ To: john@email.com                  │ │
│ │ Subject: Important Update on Your   │ │
│ │          Settlement Offer           │ │
│ │                                     │ │
│ │ Dear John,                          │ │
│ │                                     │ │
│ │ I hope this email finds you well... │ │
│ │ [Full draft content]                │ │
│ │                                     │ │
│ │ Best regards,                       │ │
│ │ Your Legal Team                     │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ⚠️  This action requires your approval │
│                                         │
│ [✅ Approve] [✏️ Edit] [❌ Reject]      │
└─────────────────────────────────────────┘
```

#### **Scenario 3: Appointment Scheduling (Approval Required)**

```json
// User: "Schedule a meeting with the client for Thursday at 2pm"

// API Response:
{
  "status": "success",
  "action_type": "schedule_appointment",
  "requires_approval": true,
  "result": {
    "appointment_type": "Client Meeting",
    "date": "2025-10-31",
    "time": "14:00",
    "duration": "60 minutes",
    "attendees": ["John Smith", "Lawyer"],
    "notes": "Discuss settlement offer details"
  },
  "activity_logged": true,
  "activity_id": "act-20251026-abc"
}

// Frontend Display:
┌─────────────────────────────────────────┐
│ 👤 You: Schedule a meeting with the    │
│         client for Thursday at 2pm      │
├─────────────────────────────────────────┤
│ 🤖 AI: I've prepared an appointment     │
│        request:                         │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 📅 Appointment Details              │ │
│ │ ─────────────────────────────────── │ │
│ │ Type: Client Meeting                │ │
│ │ Date: Thursday, October 31, 2025    │ │
│ │ Time: 2:00 PM - 3:00 PM             │ │
│ │ Attendees:                          │ │
│ │   • John Smith (Client)             │ │
│ │   • You (Lawyer)                    │ │
│ │                                     │ │
│ │ Notes: Discuss settlement offer     │ │
│ │        details                      │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ⚠️  This action requires your approval │
│                                         │
│ [✅ Approve] [✏️ Edit] [❌ Reject]      │
└─────────────────────────────────────────┘
```

---

## 🎨 Frontend Implementation Strategy

### **Chat Component Structure:**

```tsx
// Main Chat Interface
<CaseChatInterface case_id={caseId}>
  {/* Message History */}
  <MessageList>
    {messages.map((msg) =>
      msg.role === "user" ? (
        <UserMessage content={msg.content} />
      ) : (
        <AIMessage
          content={msg.content}
          actionType={msg.action_type}
          requiresApproval={msg.requires_approval}
          activityId={msg.activity_id}
        />
      )
    )}
  </MessageList>

  {/* Approval Cards (if needed) */}
  {pendingApprovals.map((approval) => (
    <ApprovalCard
      activity={approval}
      onApprove={() => handleApprove(approval.activity_id)}
      onReject={() => handleReject(approval.activity_id)}
      onEdit={() => handleEdit(approval.activity_id)}
    />
  ))}

  {/* Input Area */}
  <ChatInput
    onSend={handleSendMessage}
    placeholder="Ask me to research, draft emails, schedule appointments..."
  />
</CaseChatInterface>
```

### **API Integration Flow:**

```typescript
// 1. Send Message
const handleSendMessage = async (message: string) => {
  // Add user message to UI
  addMessage({ role: "user", content: message });

  // Call API
  const response = await fetch("/api/agent/process", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      case_id: caseId,
      query: message,
      session_id: currentSessionId, // Optional: continue session
    }),
  });

  const data = await response.json();

  // Add AI response to UI
  addMessage({
    role: "assistant",
    content: data.result,
    action_type: data.action_type,
    requires_approval: data.requires_approval,
    activity_id: data.activity_id,
  });

  // If requires approval, show approval card
  if (data.requires_approval) {
    addPendingApproval(data);
  }

  // Update session ID
  setCurrentSessionId(data.session_id);
};

// 2. Approve Action
const handleApprove = async (activityId: string) => {
  await fetch(`/api/activities/${activityId}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      approved_by: currentUser.email,
    }),
  });

  // Update UI
  removePendingApproval(activityId);
  addMessage({
    role: "system",
    content: "✅ Action approved and executed!",
  });
};

// 3. Reject Action
const handleReject = async (activityId: string, reason: string) => {
  await fetch(`/api/activities/${activityId}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      approved_by: currentUser.email,
      reason: reason,
    }),
  });

  // Update UI
  removePendingApproval(activityId);
  addMessage({
    role: "system",
    content: "❌ Action rejected. You can ask me to revise it.",
  });
};
```

---

## 📋 Implementation Checklist

### **Phase 1: Chat Interface (Current Sprint)**

- [ ] **Update Case Page Chat Component**

  - [ ] Integrate with `/api/agent/process` endpoint
  - [ ] Display different message types (user, AI, system)
  - [ ] Show loading states while processing
  - [ ] Handle session management (store session_id)

- [ ] **Approval Card Component**

  - [ ] Create `ApprovalCard` component for email drafts
  - [ ] Create `ApprovalCard` component for appointments
  - [ ] Add Approve/Reject/Edit buttons
  - [ ] Integrate with `/api/activities/*` endpoints

- [ ] **Message History**
  - [ ] Fetch conversation history on page load
  - [ ] Use `/api/sessions/<session_id>/messages`
  - [ ] Display past messages in chronological order
  - [ ] Auto-scroll to latest message

### **Phase 2: Enhanced Specialists (Next Sprint)**

- [ ] **Records Wrangler Agent**

  - [ ] Create agent in backend
  - [ ] Add `request_records` action type
  - [ ] Integrate with email/SMS APIs
  - [ ] Add to orchestrator routing

- [ ] **Evidence Sorter Agent**

  - [ ] Create agent in backend
  - [ ] Add `organize_evidence` action type
  - [ ] Integrate with Salesforce API
  - [ ] Auto-categorize uploaded files

- [ ] **Enhanced Legal Researcher**
  - [ ] Add web search capability (Google Custom Search API)
  - [ ] Add case law database integration
  - [ ] Improve citation formatting

### **Phase 3: Execution Layer (Future)**

- [ ] **Email Sending**

  - [ ] Integrate with email provider (SendGrid, AWS SES)
  - [ ] Add email templates
  - [ ] Track sent emails

- [ ] **Calendar Integration**

  - [ ] Integrate with Google Calendar / Outlook
  - [ ] Send calendar invites
  - [ ] Handle scheduling conflicts

- [ ] **Salesforce Integration**
  - [ ] Connect to Salesforce API
  - [ ] Auto-upload organized files
  - [ ] Sync case data

---

## 🎯 Key Insights

### **What's Already Working:**

1. ✅ **Multi-Source Input Processing**

   - PDFs, images, text files, emails all processed
   - Gemini Vision for image analysis
   - Text chunking and vector embeddings

2. ✅ **Smart AI Orchestrator**

   - Gemini-powered intent detection
   - Automatic session management
   - Context-aware routing

3. ✅ **Human-in-the-Loop**

   - Activity logging for approval-needed actions
   - Approve/Reject endpoints
   - Clean separation: research (no approval) vs. actions (approval)

4. ✅ **Conversation History**
   - All messages stored in sessions
   - Full audit trail
   - Context preservation (last 5 messages)

### **What Needs Building:**

1. 🔨 **Frontend Chat UI**

   - Message display components
   - Approval card components
   - Session management in React

2. 🔨 **Additional Specialists**

   - Records Wrangler
   - Evidence Sorter
   - Enhanced Legal Researcher

3. 🔨 **Execution Layer**
   - Actual email sending
   - Calendar integration
   - Salesforce sync

---

## 🚀 Next Steps

### **Immediate (This Session):**

1. **Update Case Page Chat**

   - Replace placeholder chat with real API integration
   - Add message types (user, AI, approval)
   - Implement send message functionality

2. **Create Approval Components**

   - Email draft approval card
   - Appointment approval card
   - Approve/Reject handlers

3. **Test Workflow**
   - Test research queries (no approval)
   - Test email drafts (with approval)
   - Test appointment scheduling (with approval)

### **Short Term (Next Sprint):**

1. Build Records Wrangler agent
2. Build Evidence Sorter agent
3. Add web search to Legal Researcher
4. Improve UI/UX for approval flow

### **Long Term (Future Sprints):**

1. Add actual email sending
2. Add calendar integration
3. Add Salesforce integration
4. Add voice transcription for call notes

---

## 💡 Pro Tips

1. **Keep It Simple First**

   - Start with the chat interface showing AI responses
   - Add approval cards as separate components
   - Don't overcomplicate the UI

2. **Leverage Existing API**

   - The backend is already smart (session management, routing)
   - Frontend just needs to display and handle approvals
   - Don't rebuild logic that exists in backend

3. **User Experience**

   - Show loading states ("AI is thinking...")
   - Show typing indicators
   - Auto-scroll to new messages
   - Clear visual distinction for approval-needed items

4. **Error Handling**
   - Handle API failures gracefully
   - Allow retry on failed messages
   - Show helpful error messages

---

## 📞 API Endpoints Quick Reference

| Action         | Endpoint                                | Method | Purpose                            |
| -------------- | --------------------------------------- | ------ | ---------------------------------- |
| Send Message   | `/api/agent/process`                    | POST   | Chat with AI, get routed response  |
| Get Activities | `/api/activities/<case_id>`             | GET    | Get approval-needed items for case |
| Approve Action | `/api/activities/<activity_id>/approve` | POST   | Approve pending action             |
| Reject Action  | `/api/activities/<activity_id>/reject`  | POST   | Reject pending action              |
| Get Sessions   | `/api/sessions/<case_id>`               | GET    | Get conversation sessions          |
| Get Messages   | `/api/sessions/<session_id>/messages`   | GET    | Get full conversation history      |
| End Session    | `/api/sessions/<session_id>/end`        | POST   | Mark session as completed          |

---

**Ready to implement? Let's start with updating the case page chat interface!** 🚀
