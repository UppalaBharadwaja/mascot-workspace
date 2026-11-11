# MASCoT Public Deployment Guide

This guide details step-by-step instructions for deploying MASCoT into production using **Vercel** (Frontend), **Render** (Backend API & Streamable HTTP MCP Server), and **Render/Supabase** (Managed PostgreSQL).

---

## Architecture Topology in Production

```
Customer's Claude ────(Streamable HTTP /mcp)────► MASCoT MCP Server (Render)
                                                        │
                                                        ▼ (REST API)
User Browser ──────────(HTTPS)───────────────► MASCoT Backend API (Render)
   (Vercel)                                             │
                                                        ▼ (SQLAlchemy / TLS)
                                              PostgreSQL Database (Supabase/Render)
```

---

## 1. Database Provisioning (Managed PostgreSQL)

### Option A: Render Managed PostgreSQL
1. Log into [Render Dashboard](https://dashboard.render.com).
2. Click **New + > PostgreSQL**.
3. Name: `mascot-db`.
4. Region: Choose closest to your target audience (e.g., Oregon or Frankfurt).
5. Plan: **Free** tier.
6. Once provisioned, copy the **Internal Database URL** (for Render services) and **External Database URL**.

### Option B: Supabase PostgreSQL
1. Create a free project at [supabase.com](https://supabase.com).
2. Navigate to **Project Settings > Database > Connection Strings > URI**.
3. Copy the connection URI: `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres`.
*(Note: MASCoT's `database.py` automatically handles converting legacy `postgres://` URLs to `postgresql://`)*.

---

## 2. Deploying Backend API (Render)

1. Connect your GitHub/GitLab repository to Render.
2. Click **New + > Web Service**.
3. Configure the service:
   - **Name**: `mascot-api`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
4. Set Environment Variables:
   - `DATABASE_URL`: Your PostgreSQL connection string.
   - `CORS_ORIGINS`: `*` (or your production Vercel domain, e.g., `https://mascot.vercel.app`).
5. Click **Create Web Service**.
6. Note down the public URL: `https://mascot-api.onrender.com`.
7. Verify by opening `https://mascot-api.onrender.com/health` in your browser. Expected: `{"status": "ok", "service": "mascot-api", "database": "connected"}`.

---

## 3. Deploying MCP Server (Render)

1. In Render Dashboard, click **New + > Web Service**.
2. Select the same repository.
3. Configure the service:
   - **Name**: `mascot-mcp`
   - **Root Directory**: `mcp_server`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python server.py`
4. Set Environment Variables:
   - `BACKEND_URL`: `https://mascot-api.onrender.com` (Your backend public URL from Step 2).
   - Render automatically provides `PORT`.
5. Click **Create Web Service**.
6. The public Streamable HTTP MCP endpoint is: `https://mascot-mcp.onrender.com/mcp`.

---

## 4. Deploying Frontend Application (Vercel)

1. Log into [Vercel](https://vercel.com) and click **Add New... > Project**.
2. Import the Git repository.
3. Configure the build settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add Environment Variable:
   - `VITE_API_URL`: `https://mascot-api.onrender.com` (Your backend URL).
5. Click **Deploy**.
6. Open your live application at `https://<YOUR-PROJECT>.vercel.app`.

---

## 5. Automated Blueprint Deployment (render.yaml)

Alternatively, you can deploy both backend and MCP server along with a database simultaneously using Render's Infrastructure-as-Code Blueprint:
1. In Render, select **Blueprints**.
2. Select the repository containing `render.yaml`.
3. Render will automatically configure:
   - `mascot-api`
   - `mascot-mcp`
   - `mascot-db`
4. Connect their environment variables automatically.

---

## 6. Security Limitations & Production Readiness Roadmap

> [!WARNING]
> This MVP is designed to demonstrate external Claude integration via MCP without in-app AI. It is intentionally unauthenticated to allow seamless evaluation. Before handling proprietary enterprise sales records or customer PII, implement the following security layers:

1. **User Authentication & Authorization**:
   - Implement OAuth2 / OIDC (e.g., Supabase Auth, Clerk, Auth0) on both the web application and API endpoints.
   - Restrict access to authorized sales representatives.
2. **Multi-Tenant Data Isolation**:
   - Add `organization_id` and `user_id` foreign keys to the `CompanyBrief` model.
   - Enforce row-level security (RLS) in PostgreSQL.
3. **MCP Token Authentication**:
   - Authenticate incoming MCP connections via bearer tokens or API keys passed in request headers.
   - Ensure a user's Claude instance can only read and write records belonging to that user's organization.
4. **Rate Limiting & Audit Logging**:
   - Apply rate limiting on `/briefs` and `/mcp` endpoints using Redis/Upstash.
   - Maintain an append-only audit log tracking changes made via UI vs. MCP tool calls.
