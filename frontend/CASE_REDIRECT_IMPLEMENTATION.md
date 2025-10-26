# 🔄 Case Creation Redirect Implementation

## Overview

After a user creates a new case, they are automatically redirected to the newly created case's detail page. This provides immediate feedback and allows them to view/manage the case right away.

## Implementation Details

### 1. **Next.js Router Hook**

We use Next.js's `useRouter` hook from `next/navigation` to handle client-side navigation:

```typescript
import { useRouter } from "next/navigation";

const router = useRouter();
```

### 2. **AddCaseModal Component Updates**

#### Added Props:

```typescript
interface AddCaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  redirectToCase?: boolean; // New: Optional control for redirect behavior
}
```

#### Implementation in Component:

```typescript
const AddCaseModal: React.FC<AddCaseModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  redirectToCase = true, // Default to true - redirect by default
}) => {
  const router = useRouter();

  // ... rest of component logic

  const handleSubmit = async () => {
    try {
      // Create the case
      const response = await create({
        case_name: formData.caseName,
        client_name: formData.clientName,
        // ... other fields
      });

      // Store case info
      setCreatedCaseId(response.case_id);
      setCreatedCaseNumber(response.case_number);

      // Show success animation
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Reset form
      // ...

      // Call success callback
      if (onSuccess) {
        onSuccess();
      }

      // Close modal
      onClose();

      // 🎯 REDIRECT TO CASE PAGE
      if (redirectToCase && response.case_id) {
        router.push(`/case/${response.case_id}`);
      }
    } catch (error) {
      // Error handling
    }
  };
};
```

## Flow Diagram

```
User fills form → Clicks Submit → API creates case
                                         ↓
                                  Returns case_id
                                         ↓
                                  Show success animation (2s)
                                         ↓
                                  Reset form & close modal
                                         ↓
                                  Call onSuccess() callback
                                         ↓
                                  router.push(`/case/${case_id}`)
                                         ↓
                                  User sees case detail page
```

## URL Structure

The case detail page uses Next.js dynamic routes:

```
/case/[slug]/page.tsx
```

When a case is created with `case_id = "case-a1b2c3d4-e5f6-7890-abcd-ef1234567890"`, the user is redirected to:

```
/case/case-a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

## Usage Examples

### Example 1: Default Behavior (Redirect Enabled)

```typescript
<AddCaseModal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  onSuccess={() => {
    refetch(); // Refresh case list
  }}
  // redirectToCase defaults to true
/>
```

**Result**: After case creation, user is redirected to `/case/[case_id]`

### Example 2: Disable Redirect

```typescript
<AddCaseModal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  onSuccess={() => {
    refetch();
    // Maybe show a toast notification instead
    toast.success("Case created successfully!");
  }}
  redirectToCase={false} // Disable redirect
/>
```

**Result**: After case creation, modal closes but user stays on current page

### Example 3: Custom Redirect Logic

```typescript
<AddCaseModal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  onSuccess={() => {
    refetch();
    // Custom redirect logic in parent
    router.push("/cases"); // Go to cases list instead
  }}
  redirectToCase={false} // Disable default redirect
/>
```

**Result**: User is redirected to custom location defined in parent

## Benefits

### 1. **Immediate Feedback**

- User sees their newly created case right away
- Confirms the case was created successfully
- Shows all case details including uploaded files

### 2. **Better UX Flow**

- Natural progression: Create → View → Manage
- Reduces clicks (no need to search for the case)
- Keeps user engaged with the application

### 3. **Flexibility**

- `redirectToCase` prop allows disabling redirect when needed
- Parent component can override with custom logic via `onSuccess`
- Works seamlessly with existing callback system

### 4. **Type Safety**

- TypeScript ensures `case_id` exists before redirect
- Proper error handling if API fails
- No redirect on error (user stays on modal to retry)

## Technical Details

### Router Methods Used

```typescript
// Client-side navigation (no page reload)
router.push("/case/123");

// Alternative methods available:
router.replace("/case/123"); // Replace current history entry
router.back(); // Go back
router.forward(); // Go forward
router.refresh(); // Refresh current route
```

### Timing

```typescript
// Wait 2 seconds to show success animation
await new Promise((resolve) => setTimeout(resolve, 2000));

// Then close modal
onClose();

// Then redirect (happens after modal close animation)
router.push(`/case/${case_id}`);
```

This timing ensures:

1. User sees success feedback
2. Modal closes smoothly
3. Navigation happens cleanly

## Error Handling

```typescript
try {
  const response = await create({ ... });

  // ... success flow with redirect

} catch (error) {
  console.error("Error creating case:", error);
  setIsCreating(false);
  alert(createError || "Failed to create case. Please try again.");
  // ❌ No redirect on error - user stays on modal to retry
}
```

## Integration with Existing Code

### Home Page (`src/app/page.tsx`)

```typescript
<AddCaseModal
  isOpen={isAddCaseModalOpen}
  onClose={() => setIsAddCaseModalOpen(false)}
  onSuccess={() => {
    refetch(); // Refresh case list
  }}
  // redirectToCase defaults to true
/>
```

### Cases Page (`src/app/cases/page.tsx`)

```typescript
<AddCaseModal
  isOpen={isAddCaseModalOpen}
  onClose={() => setIsAddCaseModalOpen(false)}
  onSuccess={() => {
    refetch(); // Refresh case list
  }}
  // redirectToCase defaults to true
/>
```

Both pages will now redirect to the case detail page after creation.

## Future Enhancements

### 1. **Toast Notifications**

```typescript
// Show toast before redirect
toast.success(`Case ${response.case_number} created!`);
router.push(`/case/${response.case_id}`);
```

### 2. **Query Parameters**

```typescript
// Add query param to show success message on case page
router.push(`/case/${response.case_id}?created=true`);
```

### 3. **Smooth Transitions**

```typescript
// Add page transition animation
router.push(`/case/${response.case_id}`, { scroll: true });
```

### 4. **Prefetching**

```typescript
// Prefetch case page data while showing success animation
router.prefetch(`/case/${response.case_id}`);
await new Promise((resolve) => setTimeout(resolve, 2000));
router.push(`/case/${response.case_id}`);
```

## Testing

### Manual Testing Steps:

1. **Test Default Redirect:**

   - Click "Add Case" button
   - Fill in case information
   - Upload files (optional)
   - Click through to submit
   - ✅ Verify redirect to `/case/[case_id]`

2. **Test Disabled Redirect:**

   - Set `redirectToCase={false}` in parent
   - Create a case
   - ✅ Verify modal closes but no redirect

3. **Test Error Handling:**

   - Stop backend server
   - Try to create case
   - ✅ Verify error shown, no redirect, modal stays open

4. **Test URL Format:**
   - Create a case
   - ✅ Verify URL is `/case/case-[uuid]`
   - ✅ Verify case page loads correctly

## Summary

✅ **Implemented**: Automatic redirect to case detail page after creation  
✅ **Configurable**: Can be disabled via `redirectToCase` prop  
✅ **Smooth UX**: 2-second success animation before redirect  
✅ **Error Safe**: No redirect on error, user can retry  
✅ **Type Safe**: TypeScript ensures `case_id` exists  
✅ **Flexible**: Parent can override with custom logic

The redirect implementation provides a seamless user experience while maintaining flexibility for different use cases.
