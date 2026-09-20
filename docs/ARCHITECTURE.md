# Python LMS Architecture

## Phase 0 repository assessment

The workspace was created as a new project because `C:\Users\nitee\Downloads` contained no LMS repository, Git metadata, frontend, backend, database, authentication, deployment configuration, or reusable LMS assets. The nearby Flask salary-prediction application is unrelated and is intentionally untouched.

## Product scope

The platform serves learners studying Python, instructors authoring and grading learning content, and administrators operating the marketplace. A course is composed of ordered modules and lessons. Lessons may be video, rich text, coding exercises, quizzes, assignments, or projects. Enrollment grants access, while progress is captured at lesson and course level. Paid enrollments are created only from verified payment-provider events.

## Architecture decisions

Use a Django-centered monorepo. The Phase 1 implementation intentionally replaces the earlier provisional NestJS/Next.js choice with Django/DRF and a Vite React client.

```text
Browser / mobile web
        |
   React + TypeScript + Vite web app
        |
  HTTPS REST API + webhook endpoints
        |
 Django + Django REST Framework API
   |        |          |          |
PostgreSQL Redis    S3/R2       Celery workers
                  (media/files) (emails, certificates,
                                  analytics, webhooks)
```

| Concern | Selected design | Reason |
| --- | --- | --- |
| Web UI | React, TypeScript, Vite, Tailwind CSS | Fast development, accessible responsive component foundation |
| API | Django, Django REST Framework, drf-spectacular | Mature Python ecosystem, explicit serializers and schema generation |
| Primary data | PostgreSQL | Transactions for orders/enrollments and strong relational integrity |
| Cache/jobs | Redis + Celery | Rate limiting, ephemeral state, asynchronous reliable work |
| Assets | S3-compatible object storage + CDN | Scalable video/file delivery; the API never streams large media |
| Video | Mux or Cloudflare Stream | Signed playback, adaptive streaming, webhooks |
| Code execution | Isolated runner service with Firecracker/gVisor sandbox | Never run learner Python inside API containers |
| Payments | Stripe Checkout/Payment Intents with verified webhooks | PCI scope reduction and idempotent fulfillment |
| Search | PostgreSQL full-text initially; Meilisearch/OpenSearch adapter at scale | Low operational cost, replaceable search boundary |
| Observability | OpenTelemetry, structured logs, Sentry, Prometheus/Grafana | Trace request-to-worker behavior and detect failures |

## Service boundaries

The first release is a modular monolith: one deployable API with independently testable modules and a separate worker process. This preserves transaction safety and development speed. Modules communicate through application events persisted in an outbox table; high-volume modules can later be extracted without changing clients.

- **Identity**: registration, sessions, roles, profile, password reset, email verification.
- **Catalog**: categories, courses, instructor attribution, publishing and discovery.
- **Learning**: modules, versioned lessons, progress, coding submissions, quizzes.
- **Assessment**: assignments/projects, rubric grading, instructor feedback.
- **Commerce**: prices, coupons, orders, payments, refunds, entitlement fulfillment.
- **Credentials**: completion evaluation, certificate issuance and public verification.
- **Engagement**: in-app/email notifications, reviews, search indexing.
- **Operations**: analytics rollups, audit logs, moderation, platform settings.

## Authorization model

Use role-based access control with ownership checks:

- `student`: browse, purchase, learn, submit work, review owned course enrollment.
- `instructor`: author and manage only assigned courses; grade enrolled students.
- `admin`: platform-wide operations, refunds, moderation, analytics, user controls.
- `support` (optional): read-only support access, no payment secrets or content changes.

Server-side policies are mandatory: UI visibility is never authorization. Course authoring has draft/review/published/archived states. Learners see only published content and only content allowed by their active enrollment.

## Key workflows

1. **Purchase**: cart validates price and coupon server-side → API creates an idempotent pending order → hosted payment flow → verified webhook records payment and grants enrollment in one transaction → queue sends receipt and enrollment notification.
2. **Learning**: client requests entitlement-checked lesson payload → video URL is short-lived and signed → progress events are deduplicated and bounded → completion is calculated server-side.
3. **Assessment**: learner submits versioned answer/files/code → async sandbox test run or instructor review → immutable grade record → recalculated course completion.
4. **Certificate**: completion policy passes → worker generates immutable certificate with random verification code → public verification exposes only opted-in minimal information.

## Folder structure

```text
python-lms/
  backend/
    config/                 # Django settings, routes, Celery configuration
    apps/                   # Django application modules
    requirements/           # locked dependency inputs by environment
  frontend/                 # Vite React + TypeScript + Tailwind client
  infra/
    docker/
    terraform/
    kubernetes/
  docs/
  tests/                    # cross-service E2E/performance tests (future)
  .github/workflows/
```

## Non-functional requirements and scale

Stateless web/API containers scale horizontally. PostgreSQL uses connection pooling, read replicas for analytics/search reads when justified, point-in-time recovery, and partitioning for very large event tables. Redis holds no source-of-truth data. Object storage has lifecycle policies. Paginated APIs use cursor pagination; expensive analytics are pre-aggregated. All event consumers are idempotent.

Initial SLO targets: 99.9% monthly API availability, p95 read API under 300 ms excluding third parties, p95 write API under 600 ms, RPO under 15 minutes, and RTO under 4 hours. These targets are verified with monitoring and disaster-recovery exercises.
