# Frontend Architecture & Implementation Guide

## 1. Tech Stack
- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS + Shadcn UI
- **State Management**: Zustand or Redux Toolkit
- **Real-Time**: Socket.io-client (or native WebSocket)

## 2. Directory Structure
```
frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── signup/page.tsx
│   ├── (dashboard)/
│   │   ├── restaurant/page.tsx
│   │   └── rider/page.tsx
│   ├── order/[id]/page.tsx
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── ui/
│   ├── Map.tsx
│   ├── MenuCard.tsx
│   └── Chatbot.tsx
├── lib/
│   ├── api.ts (Axios instances)
│   └── socket.ts (WebSocket connection)
```

## 3. Key Pages

### A. Home Page
- Hero section with search bar (AI-powered text input).
- "Recommended for You" section (fetched from `ai_engine`).
- Category slider.

### B. Restaurant Page
- Menu list grouped by categories.
- "Add to Cart" with variation selection modal.

### C. Checkout
- Address selection (Google Maps integration).
- Payment gateway iframe (Stripe/Razorpay).

### D. Order Tracking (`/order/[id]`)
- Connects to `ws://backend/ws/orders/[id]/`.
- Updates status steps (Placed -> Accepted -> ...).
- Shows map with Rider icon moving in real-time.

### E. Rider App
- Toggle "Available" status.
- "New Order" pop-up with Accept/Reject.
- Navigation view.

## 4. Integration Details
- **Auth**: Store JWT in HttpOnly cookies or localStorage.
- **Maps**: Use `react-google-maps/api` or `leaflet`.
- **WebSockets**:
  ```javascript
  const socket = new WebSocket('ws://localhost:8000/ws/orders/123/');
  socket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === 'order_status') {
          updateStatus(data.status);
      }
  };
  ```
