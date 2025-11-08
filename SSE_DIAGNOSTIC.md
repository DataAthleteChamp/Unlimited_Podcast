# SSE Connection Diagnostic

## What Was Fixed

### 1. Backend Reloading Issue ✅
**Problem**: Backend was constantly reloading every ~20 seconds due to uncommitted changes in `content_generator.py`

**Fix**: Committed the Dust integration changes to stop WatchFiles from detecting file changes

### 2. Added SSE Diagnostic Logging ✅
**File**: `endlesspodcast/src/hooks/useSSE.ts`

**Added logging**:
```typescript
// When SSE mounts
console.log('🔵 [SSE] useEffect MOUNTING - Creating new EventSource');

// When SSE unmounts
console.log('🔴 [SSE] useEffect UNMOUNTING - Closing EventSource');
console.trace('🔴 [SSE] Stack trace for unmount:');
```

This will help identify **exactly** what's causing the SSE to disconnect.

---

## How to Test

### 1. Both Servers Are Running

**Backend** (Terminal 1): ✅ Running on http://localhost:8000
```
INFO: Application startup complete.
```

**Frontend** (Terminal 2): ✅ Running on http://localhost:8080
```
VITE v5.4.19  ready in 142 ms
➜  Local:   http://localhost:8080/
```

### 2. Open Browser

1. Navigate to: **http://localhost:8080**
2. Open DevTools: Press **F12** or **Cmd+Option+I**
3. Go to **Console** tab

### 3. Watch the Logs

#### Expected Behavior (Working)

**Frontend Console**:
```
🔵 [SSE] useEffect MOUNTING - Creating new EventSource
✅ SSE connected successfully
```

**Backend Terminal**:
```
INFO: 127.0.0.1:xxxxx - "GET /api/stream HTTP/1.1" 200 OK
backend.api.stream - INFO - New SSE client connected
```

Then **NO MORE** mount/unmount logs unless you refresh the page.

#### Problem Behavior (Still Disconnecting)

**Frontend Console** (repeating every 5 seconds):
```
🔵 [SSE] useEffect MOUNTING - Creating new EventSource
✅ SSE connected successfully
🔴 [SSE] useEffect UNMOUNTING - Closing EventSource
console.trace Stack trace for unmount:
    at <STACK TRACE HERE>
```

**Backend Terminal** (repeating):
```
INFO: SSE client disconnected
INFO: New SSE client connected
```

### 4. Analyze the Stack Trace

If you see the unmounting logs, the **stack trace** will tell us exactly what's triggering the component to remount:

- **HMR (Hot Module Replacement)**: File changes causing remounts
- **React component remounting**: Parent component re-rendering
- **Browser extension**: DevTools or extensions interfering
- **Navigation**: React Router navigating

---

## Current Architecture

### SSE Hook (`useSSE.ts`)

```typescript
// ✅ Callbacks stored in ref - doesn't trigger reconnect
const callbacksRef = useRef(options);

useEffect(() => {
  callbacksRef.current = {
    onTopicsUpdated,
    onNowPlaying,
    onChatMessage
  };
}, [onTopicsUpdated, onNowPlaying, onChatMessage]);

// ✅ Empty deps - connects ONCE on mount only
useEffect(() => {
  const es = api.createEventSource();
  eventSourceRef.current = es;

  es.addEventListener('CHAT_MESSAGE', (event) => {
    // Uses ref, not direct callback
    callbacksRef.current.onChatMessage?.(JSON.parse(event.data));
  });

  return () => {
    es.close(); // Only on unmount
  };
}, []); // Empty deps - NEVER reconnect
```

### SSE Usage (Index.tsx)

```typescript
// ✅ SINGLE SSE connection for entire app
useSSE({
  onTopicsUpdated: () => refetch(),
  onChatMessage: (data) => {
    // Dispatches to ChatSidebar via window event
    window.dispatchEvent(new CustomEvent('chat-message', { detail: data }));
  },
  autoConnect: true,
});
```

### ChatSidebar

```typescript
// ✅ NO SSE connection here - listens to window events
useEffect(() => {
  window.addEventListener('chat-message', handleChatMessage);
  return () => window.removeEventListener('chat-message', handleChatMessage);
}, []);
```

---

## Possible Causes (If Still Disconnecting)

### 1. React Development Mode
**Issue**: Some React features cause double-rendering in dev mode

**Check**: `src/main.tsx` - We verified NO `<React.StrictMode>` is used ✅

### 2. Hot Module Replacement (HMR)
**Issue**: Vite HMR might be reloading components when files change

**Test**:
- Stop editing files for 30 seconds
- See if disconnections stop
- If they do, HMR is the cause

**Solution**: Build production version to test without HMR:
```bash
cd /Users/jakubpiotrowski/PycharmProjects/endlesspodcast
npm run build
npm run preview
```

### 3. React Query Refetching
**Issue**: `refetchInterval: 5000` in Index.tsx might be causing re-renders

**Current code**:
```typescript
const { data: backendTopics = [], refetch } = useQuery<Topic[]>({
  queryKey: ['topics'],
  queryFn: () => api.getTopics(),
  refetchInterval: 5000, // Refetch every 5 seconds
});
```

**Test**: If disconnections happen every 5 seconds, this might be the cause

**Solution**: Remove `refetchInterval` and rely only on SSE for updates:
```typescript
const { data: backendTopics = [], refetch } = useQuery<Topic[]>({
  queryKey: ['topics'],
  queryFn: () => api.getTopics(),
  // No refetchInterval - SSE will trigger refetch()
});
```

### 4. Multiple Browser Tabs
**Issue**: Opening multiple tabs creates multiple SSE connections

**Test**: Ensure only ONE tab is open to http://localhost:8080

### 5. Browser Extensions
**Issue**: React DevTools or other extensions might be interfering

**Test**: Open in incognito mode without extensions

---

## Next Steps

1. **Open browser** to http://localhost:8080
2. **Check console logs** for mount/unmount messages
3. **Share the results**:
   - If you see 🔵 MOUNTING once and no 🔴 UNMOUNTING → **Fixed!** ✅
   - If you see 🔴 UNMOUNTING repeatedly → **Share the stack trace**
4. Based on stack trace, we'll identify the root cause

---

## Quick Reference

**Backend**: http://localhost:8000
**Frontend**: http://localhost:8080
**Backend Logs**: Terminal 1 (where you ran `python -m backend.main`)
**Frontend Logs**: Browser Console (F12 → Console)

**Both servers must be running for SSE to work!**
