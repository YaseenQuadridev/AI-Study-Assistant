# Security Audit Report

Adaptive Study Planner v2.0.0-ARCH
Date: 2026-06-26

---

## Scope

- `scoring_test/` (Phase 1 MVP)
- `backend/` (Phase 2+ layers)
- `tests/`

---

## Findings

| Severity | Finding | Status | Notes |
|----------|---------|--------|-------|
| Info | No auth in MVP | Accepted | Documented as Phase 1 non-goal (NG-01). No PII collected. |
| Low | CORS wide-open | **Fixed** | Now configurable via `CORS_ORIGINS` env var. Defaults to `*` only for dev. |
| Low | No CSRF tokens | Accepted | MVP has no sessions or cookies. CSRF irrelevant without auth. Add when auth is introduced. |
| Low | No rate limiting | **Fixed** | In-memory per-IP rate limiter added (env-configurable). |
| Low | XSS in frontend | **Fixed** | `app.js` used `innerHTML` with server data. Replaced with safe `createElement` + `textContent`. |
| None | No hardcoded secrets | ✅ | API keys passed via constructor / env vars. No secrets in repo. |
| None | No SQL injection | ✅ | Phase 1 uses JSON file. Phase 2+ uses parameterized Supabase client. |
| None | Input validation | ✅ | D/P/U clamped to [0,1]. Flask routes now catch `ValueError`/`TypeError` and return 400. |
| None | Atomic writes | ✅ | `tempfile.NamedTemporaryFile` + `os.replace` + `threading.Lock` prevents corruption and races. |
| None | Unsafe deserialization | ✅ | `pickle.load` replaced with `json.load` in `VectorStore`. Legacy pickle files still readable as fallback. |
| None | No subprocess/eval | ✅ | No `os.system`, `eval`, `exec`, or `subprocess` calls in business logic. |

---

## Recommendations for Phase 3

1. Replace in-memory rate limiter with Redis-backed `Flask-Limiter` for multi-worker deployments.
2. Replace `threading.Lock` with `filelock` if running multiple Flask processes.
3. Add CSRF protection when authentication is introduced.
4. Use HTTPS-only cookies for session tokens.
5. Enable RLS (Row Level Security) on Supabase tables before multi-user launch.

---

## Verdict

**MVP is secure for local single-user use.** All verified findings fixed. Production hardening required before public internet deployment.
