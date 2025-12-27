# System Architecture: AI-Powered Real-Time Food Ordering & Delivery Platform

## 1. High-Level Overview
The platform is designed as a monolithic-first architecture (scalable to microservices) using **Django** for the backend and **React/Next.js** for the frontend. It relies heavily on **WebSockets (Django Channels)** for real-time features and **Redis** for high-performance data handling.

## 2. Core Components

### A. Client Layer (Frontend)
1.  **Customer Web/App (Next.js/React):**
    *   Server-Side Rendering (SSR) for SEO (Menus, Restaurants).
    *   PWA capabilities for mobile-like experience.
    *   WebSockets for live order tracking.
2.  **Restaurant Dashboard (React):**
    *   Real-time order acceptance interface.
    *   Menu management and Analytics charts.
3.  **Delivery Partner App (PWA/React):**
    *   Geolocation tracking.
    *   Order assignment notifications.
4.  **Admin Portal (Django Admin + Custom React Views):**
    *   Global oversight and configuration.

### B. Application Layer (Backend - Django)
The backend is structured into modular apps:
*   **`core`**: Shared utilities, base models, authentication overrides.
*   **`accounts`**: User management (Customer, Restaurant Owner, Delivery Partner, Admin) with JWT.
*   **`restaurants`**: Restaurant profiles, geolocations, timings.
*   **`menu`**: Categories, Items, Variations, Inventory.
*   **`orders`**: Order processing, State machine (Placed -> Accepted -> ...), Cart management.
*   **`delivery`**: Rider assignment logic, Location tracking.
*   **`payments`**: Integration with Stripe/Razorpay, Transaction logging.
*   **`ai_engine`**: Interface with OpenAI/Gemini, Recommendation logic, Demand prediction.
*   **`notifications`**: Push notifications, SMS/Email (via Celery).

### C. Real-Time Layer (Django Channels + Redis)
*   **Protocol:** WebSockets (ws://).
*   **Message Broker:** Redis Pub/Sub.
*   **Consumers:**
    *   `OrderConsumer`: Updates order status in real-time to Customer and Restaurant.
    *   `LocationConsumer`: Streams Delivery Partner GPS coordinates to Customer.
    *   `ChatConsumer`: AI Chatbot and Customer Support.

### D. Data Layer
*   **Primary DB (PostgreSQL):** Robust relational data storage for users, orders, menus, and financial transactions. PostGIS extension for geospatial queries (finding nearby restaurants/drivers).
*   **Cache & Broker (Redis):**
    *   Caching API responses (Menus).
    *   Celery Task Queue (Async jobs like sending emails, processing AI models).
    *   Channel Layer for WebSockets.

### E. AI Layer
*   **Recommendation Engine:** Analyzes `Order` and `Review` history to suggest `MenuItem`s.
*   **Demand Prediction:** Cron jobs (Celery) analyze historical order data to predict surge hours.
*   **Chatbot:** API wrapper around OpenAI/Gemini with system prompts context-aware of the menu.

## 3. Deployment Architecture
*   **Web Server:** Gunicorn (HTTP) + Daphne (WebSocket).
*   **Reverse Proxy:** Nginx (Handles SSL, static files, routes /ws/ to Daphne and /api/ to Gunicorn).
*   **Containerization:** Docker & Docker Compose.
*   **CI/CD:** GitHub Actions.

## 4. Scalability
*   **Horizontal Scaling:** Load balancer distributing traffic across multiple Django containers.
*   **Database Read Replicas:** For heavy read operations (browsing menus).
*   **Async Processing:** Heavy tasks offloaded to Celery workers.
