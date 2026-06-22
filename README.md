# HookHarbor ⚓

HookHarbor is a high-performance, enterprise-grade **Webhook Reliability Engine and Ingestion Gateway**. It acts as a resilient buffer between third-party webhook senders (like Stripe, Shopify, or GitHub) and your application backends. 

By decoupling webhook ingestion from payload delivery, HookHarbor guarantees that you **never drop a webhook**, even during downstream server outages, database locks, or sudden traffic spikes.

---

## 🚀 Key Features

* **Lightning-Fast Ingestion (`< 10ms`):** Written in Go, the ingestion gateway accepts payloads and immediately queues them, returning a `202 Accepted` response.
* **Durable Buffering:** Built on RabbitMQ, ensuring messages survive service restarts.
* **Resilient Retry Delivery (Exponential Backoff):** Deployed workers process webhooks and handle failures by routing messages to delay queues before retrying.
* **Dead Letter Queue (DLQ):** Webhooks exceeding max retries are safely archived in a DLQ for manual inspection and replay.
* **Control Plane Dashboard:** A FastAPI-powered administration panel and API to manage webhook endpoints, view live delivery logs, and trigger replays.
* **Kubernetes Native Autoscaling:** Configured to scale workers automatically via KEDA based on RabbitMQ queue depth.

---

## 🏗️ Architecture Overview

HookHarbor uses a polyglot microservices architecture to optimize each stage of the lifecycle:

```mermaid
graph TD
    %% Clients
    Sender[Webhook Sender <br> Stripe / Shopify] -->|1. POST Webhook| Gateway[Go Ingestion Gateway]
    
    %% Gateway
    Gateway -->|2. Verify Secret & <br> Fetch Endpoint Config| Cache[(Redis / Memory Cache)]
    Gateway -->|3. Publish Job| RMQ_Main[RabbitMQ: Main Exchange]
    Gateway -->|4. Return 202 Accepted| Sender
    
    %% Queue System
    subgraph RabbitMQ Broker
        RMQ_Main -->|Route| Q_Jobs[Main Jobs Queue]
        Q_Jobs -.->|Dead Letter on Expire| Q_DLQ[Dead Letter Queue]
        Q_Delay[Retry Delay Queues <br> TTL: 1m, 5m, 15m, 1h] -->|TTL Expired| RMQ_Main
    end
    
    %% Dispatcher
    Worker[TypeScript Dispatcher Worker] -->|5. Consume Job| Q_Jobs
    Worker -->|6. POST HTTP Request| Dest[Target Destination Server]
    
    %% Retry & Database Logic
    Worker -->|7a. Success: ACK| Q_Jobs
    Worker -->|7b. Failure: NACK to Delay Exchange| Q_Delay
    Worker -->|8. Log Result| DB[(PostgreSQL)]
    
    %% Management API
    FastAPI[FastAPI Management API] -->|Query Logs & Replays| DB
    FastAPI -->|Admin CRUD| DB
    FastAPI -->|9. Replay Dead Letters| RMQ_Main
    Admin[Developer Dashboard / CLI] -->|Manage / View| FastAPI
```

---

## 📂 Repository Structure

```text
HookHarbor/
├── hld.md                   # High-Level Architecture Design
├── lld.md                   # Low-Level Detailed Design (API, DB, Queue schemas)
├── gateway/                 # [Go] Ingestion Gateway service
├── dispatcher/              # [Node.js / TS] Webhook delivery workers
├── management-api/          # [Python / FastAPI] Control plane & Dashboard API
├── db/                      # Database migrations & schemas
├── infra/                   # Kubernetes manifests & Local Docker Compose
└── README.md                # This file
```

---

## 🛠️ Technology Stack

| Service | Technology | Role |
| :--- | :--- | :--- |
| **Ingestion Gateway** | Go | Ultra-fast HTTP ingestion, routing & publishing |
| **Message Broker** | RabbitMQ | Durable queuing, DLX, and TTL-based retry delays |
| **Dispatcher Workers** | Node.js / TypeScript | Webhook payload delivery, HTTP client, ACK/NACK management |
| **Management API** | Python / FastAPI | Control plane, endpoint configuration, metrics & logs |
| **Database** | PostgreSQL | Persistent configuration & delivery history logs |
| **Container Engine** | Docker / Kubernetes | Orchestration, local development & HPA/KEDA scaling |

---

## 🚦 Quick Start (Local Setup)

### Prerequisites
* [Docker & Docker Compose](https://www.docker.com/products/docker-desktop/)
* [Go (v1.21+)](https://golang.org/doc/install)
* [Node.js (v18+) & npm](https://nodejs.org/)
* [Python (v3.10+)](https://www.python.org/downloads/)

### 1. Run Infrastucture
Spin up PostgreSQL and RabbitMQ locally:
```bash
docker-compose -f infra/docker-compose.yml up -d
```

### 2. Set Up the Database
Apply migrations to spin up the schemas:
```bash
cd db/
# Run migration scripts (details in lld.md)
```

### 3. Start Services
Open separate terminal tabs for each service:

* **Ingestion Gateway:**
  ```bash
  cd gateway/
  go run main.go
  ```
* **Management API:**
  ```bash
  cd management-api/
  pip install -r requirements.txt
  uvicorn main:app --reload
  ```
* **Dispatcher Workers:**
  ```bash
  cd dispatcher/
  npm install
  npm run dev
  ```

---

## 📝 License

This project is open-source software licensed under the [MIT License](LICENSE).
