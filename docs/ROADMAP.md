# Implementation Roadmap

## Definition of done

Each increment includes feature tests, role/authorization tests, accessibility review, responsive behavior, telemetry, migration/rollback consideration, API documentation updates, and no critical/high unresolved security findings. No production secrets or payment fulfillment shortcuts are permitted.

## Phase 0 — discovery and design (complete)

- Inventory showed no LMS codebase to reuse; a clean workspace was selected.
- Architecture, relational schema, REST contract, security baseline, deployment model, and repository layout are documented.
- Technology baseline: Django/DRF, React/TypeScript/Vite/Tailwind, PostgreSQL, Redis/Celery, S3-compatible assets, isolated code runner, Stripe.

## Phase 1 — foundation

- Scaffold the Django/React repository, formatting/lint/typecheck, environment validation, Docker Compose, and production container configuration.
- Implement Django database settings, Redis/Celery settings, health endpoint, API routing, test harness, and minimal responsive React/Tailwind shell.
- Build account registration/login/verification/password recovery/session management, RBAC, profile, audit logging, and admin MFA foundation.

**Exit criteria:** a new user can safely create, verify, sign into, and revoke a session; CI passes unit/integration/E2E auth tests.

**Current implementation status:** infrastructure, API/worker configuration, health checks, a responsive React shell, Docker development/production definitions, backend linting, and backend tests are implemented. Authentication remains deliberately deferred: it is not required for the narrowly scoped runtime foundation and will be the first functional module added after full-stack environment verification.

## Phase 2 — catalog and authoring

- Build public responsive catalog/search/course pages and learner/instructor layouts.
- Implement course, module, lesson, asset, instructor, draft/review/publish lifecycle, revisioning, and admin approval APIs/UI.
- Add accessible rich-text authoring and media upload/processing status.

**Exit criteria:** an instructor can author a reviewed course and an admin can publish it; anonymous visitors can find only published content.

## Phase 3 — learning and assessment

- Course player; secure video/text/code lesson delivery; progress model; prerequisites; learner dashboard.
- Quiz authoring/attempts/grading and assignment/project submission/review/rubrics.
- Implement and independently security-test isolated Python runner, then certificate generation/verification.

**Exit criteria:** an enrolled learner completes a realistic course path including a quiz and coding submission, receives reliable progress and a verifiable certificate.

## Phase 4 — commerce and engagement

- Price history, coupons, cart/quote, Stripe checkout, webhook event processing, orders, invoices/receipts, refunds and entitlement policy.
- Notifications, reviews/moderation, search indexing, course recommendations placeholder, and transactional emails.

**Exit criteria:** payment is fulfilled only by replay-safe verified webhooks; coupon/refund/enrollment edge cases have integration tests.

## Phase 5 — operations and scale readiness

- Instructor/admin analytics, daily aggregates, audit dashboards, exports, support workflows, observability dashboards, alerts, load tests, backup restore test, and disaster-recovery runbook.
- Complete security review, accessibility audit (WCAG 2.2 AA target), penetration test remediation, performance budgets, deployment rehearsal, and production go-live checklist.

**Exit criteria:** staged release meets SLO/load/security/accessibility acceptance criteria and supports rollback/restore procedures.

## Initial test strategy

| Layer | Tooling | Coverage focus |
| --- | --- | --- |
| Unit | Vitest | domain rules, discounts, completion, permissions |
| API integration | Jest/Supertest + ephemeral PostgreSQL/Redis | auth, transactions, webhooks, guards, migrations |
| UI | React Testing Library | accessibility and state behavior |
| E2E | Playwright | registration through learning/purchase/certificate workflows |
| Security | Semgrep, npm audit, Trivy, OWASP ZAP | source, dependencies, images, attack surface |
| Performance | k6 | catalog, player manifest, progress, checkout webhook throughput |
