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
| Low | CORS wide-open | Accepted | `flask-cors` allows all origins. Acceptable for local dev only. Restrict in production. |
| Low | No CSRF tokens | Accepted | MVP has no sessions. Add CSRF + session middleware in Phase 3. |
| Low | No rate limiting | Accepted | Add Flask-Limiter in Phase 2.5+ before cloud exposure. |
| None | No hardcoded secrets | ✅ | API keys passed via constructor / env vars. No secrets in repo. |
| None | No SQL injection | ✅ | Phase 1 uses JSON file. Phase 2+ uses parameterized Supabase client. |
| None | Input validation | ✅ | D/P/U clamped to [0,1], P capped at 0.9, U floored at 0.2. |
| None | Atomic writes | ✅ | `tempfile.NamedTemporaryFile` + `os.replace` prevents corruption. |
| None | No XSS vector | ✅ | Jinja2 auto-escapes HTML. JS uses `textContent`, not `innerHTML`. |
| None | No subprocess/eval | ✅ | No `os.system`, `eval`, `exec`, or `subprocess` calls in business logic. |

---

## Recommendations for Phase 2+

1. Add `Flask-Limiter` before exposing to internet.
2. Restrict CORS to specific origins in production.
3. Add CSRF protection when auth is introduced (Phase 3).
4. Use HTTPS-only cookies for session tokens.
5. Enable RLS (Row Level Security) on Supabase tables before multi-user launch.

---

## Verdict

**MVP is secure for local single-user use.** No critical vulnerabilities found. Production hardening required before cloud deployment.
