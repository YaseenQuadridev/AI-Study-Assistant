# Phase 3: Multi-User Platform

## Overview

Phase 3 advances the Adaptive Study Planner from a single-user local tool to a multi-user cloud platform.

## Deliverables

### 1. Multi-User Database Schema

**Tables:**
- `topics` — now has `user_id` (UUID) + RLS policies
- `documents` — per-user with RLS
- `chunks` — per-user with RLS
- `app_state` — per-user composite key `(user_id, key)`
- `user_profiles` — auto-created on signup via trigger
- `study_groups` — collaborative groups
- `group_members` — group membership with roles (admin/moderator/member)
- `shared_topics` — topic sharing (user-to-user or group)

**RLS Policies:**
- All tables have `ENABLE ROW LEVEL SECURITY`
- Users can only access their own data
- Group data shared with members
- Shared topics accessible to recipients

**Migration:** `migrations/phase3_multi_user_schema.sql`

### 2. Supabase Edge Function

**Function:** `process-document`
- Parses uploaded documents into semantic chunks
- Stores chunks in the `chunks` table with `user_id`
- Updates document status from `processing` → `ready`
- Secured with JWT verification

**Deploy:** Already deployed to `blowpaeftobvczysekrr.supabase.co`

**Invoke:**
```bash
curl -X POST https://blowpaeftobvczysekrr.supabase.co/functions/v1/process-document \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"document_id": 1, "user_id": "..."}'
```

### 3. Cloudflare Worker (API Gateway)

**File:** `cloudflare-worker/worker.js`

**Features:**
- CORS proxy for all Supabase REST API endpoints
- Edge Function proxy (`/edge/process-document`)
- Health check endpoint
- Deployed to Cloudflare's edge network (300+ locations)

**Deploy:**
```bash
cd cloudflare-worker
npm install -g wrangler
wrangler login
wrangler deploy
```

### 4. Frontend with Auth

**Files:** `frontend/index.html` + `frontend/phase3-app.js`

**Features:**
- Supabase Auth (email/password)
- Automatic session management
- Protected data routes (RLS enforced server-side)
- Study plan generation (client-side, deterministic)
- Topic CRUD via Supabase client
- Session logging with performance tracking

**Open:** `frontend/index.html` in any browser or serve with `python -m http.server 8080 --directory frontend`

### 5. Architecture (Phase 3)

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Browser   │────▶│  Cloudflare Edge  │────▶│  Supabase Edge   │
│  (frontend) │     │  (Worker / CDN)   │     │  (Auth / DB)     │
└─────────────┘     └──────────────────┘     └──────────────────┘
                            │                          │
                            │                   ┌──────┴──────┐
                            │                   │ PostgreSQL  │
                            │                   │ + pgvector  │
                            │                   └─────────────┘
                            │
                     ┌──────▼──────┐
                     │  R2 Storage │ (when enabled)
                     │  (Documents)│
                     └─────────────┘
```

## Security

- **RLS enabled** on all tables
- **JWT verification** on Edge Functions
- **CORS configurable** via Worker
- **Row-level isolation** — users cannot see each other's data
- **Group sharing** via explicit shared_topics table with permission levels

## Next Steps

1. Enable Cloudflare R2 in dashboard for document storage
2. Configure OAuth providers (Google, GitHub) in Supabase Auth
3. Deploy Cloudflare Worker with `wrangler deploy`
4. Add real-time subscriptions (Supabase Realtime) for collaborative editing
5. Add AI inference via Workers AI (BAAI/BGE embeddings at edge)

## Links

- **Supabase Project:** `blowpaeftobvczysekrr`
- **Cloudflare Account:** `ff42f7b54f53ec415f8d196d19501f32`
- **Frontend:** `frontend/index.html`
- **Worker:** `cloudflare-worker/worker.js`
- **Edge Function:** `process-document`
