# REST API Specification

Base URL: `/api/v1`. JSON requests/responses use UTF-8. All protected endpoints require an HTTP-only secure session cookie or `Authorization: Bearer <access-token>`. Mutating requests require an idempotency key where indicated. OpenAPI 3.1 will be generated from Django REST Framework serializers and published at `/api/docs` outside production or behind admin authentication.

## Conventions

- Cursor lists: `{ "data": [], "page": { "nextCursor": "..." } }`.
- Errors: `{ "error": { "code": "VALIDATION_ERROR", "message": "...", "requestId": "...", "details": [] } }`.
- Status codes: 400 malformed, 401 unauthenticated, 403 unauthorized, 404 absent/not visible, 409 state conflict, 422 valid but unacceptable, 429 rate limited.
- IDs are UUIDs. Authorization filters visibility before resource lookup where needed to avoid enumeration.

## Authentication and account

| Method/path | Purpose |
| --- | --- |
| `POST /auth/register` | Register with email/password and accepted terms; sends verification email. |
| `POST /auth/login` | Login with rate limiting; creates rotating session. |
| `POST /auth/logout` | Revoke current session. |
| `POST /auth/refresh` | Rotate refresh session and issue access token. |
| `POST /auth/password/forgot` / `POST /auth/password/reset` | One-time password recovery. |
| `POST /auth/email/verify` | Consume signed verification token. |
| `GET/PATCH /me` | Retrieve/update the current profile. |
| `GET /me/sessions` / `DELETE /me/sessions/:id` | List/revoke account sessions. |

## Catalog, discovery, and reviews

| Method/path | Purpose |
| --- | --- |
| `GET /courses?query=&category=&level=&sort=&cursor=` | Public published-course search/list. |
| `GET /courses/:slug` | Public course landing page, curriculum summary, price, aggregate reviews. |
| `GET /courses/:courseId/reviews` | Moderated published reviews. |
| `POST /courses/:courseId/reviews` | Enrolled learner review; one per learner. |
| `PATCH/DELETE /courses/:courseId/reviews/me` | Update/delete own review. |
| `GET /categories` | Catalog taxonomy. |

## Learning

| Method/path | Purpose |
| --- | --- |
| `GET /me/enrollments` | Learner dashboard data and current progress. |
| `GET /enrollments/:id` | Entitlement-checked course player manifest. |
| `GET /lessons/:lessonId` | Entitlement-checked lesson payload; signed media playback data when applicable. |
| `PUT /lessons/:lessonId/progress` | Upsert progress; idempotency key required. |
| `POST /lessons/:lessonId/complete` | Request completion; server validates prerequisites. |
| `POST /quizzes/:lessonId/attempts` | Create attempt. |
| `POST /quiz-attempts/:id/submit` | Grade immutable submitted responses. |
| `POST /lessons/:lessonId/submissions` | Submit code/files/text, then queue evaluation. |
| `GET /submissions/:id` | Owner/instructor state, grade, and sanitized run output. |
| `GET /me/certificates` | Learner credentials. |
| `GET /certificates/verify/:code` | Minimal public certificate verification. |

## Instructor content and grading

All endpoints below require course-instructor ownership or admin permission.

| Method/path | Purpose |
| --- | --- |
| `POST /instructor/courses` | Create draft course. |
| `GET/PATCH /instructor/courses/:id` | Retrieve/update course metadata and completion policy. |
| `POST /instructor/courses/:id/submit-review` | Submit course for publish review. |
| `POST /instructor/courses/:id/modules` | Create ordered module. |
| `PATCH/DELETE /instructor/modules/:id` | Update/delete module. |
| `POST /instructor/modules/:id/lessons` | Create typed lesson. |
| `PATCH/DELETE /instructor/lessons/:id` | Update/delete lesson with revision. |
| `POST /instructor/assets/upload-url` | Issue constrained presigned asset upload URL. |
| `GET /instructor/courses/:id/submissions` | Queue of submissions. |
| `POST /instructor/submissions/:id/grade` | Record rubric grade and feedback. |
| `GET /instructor/analytics/courses/:id` | Enrollments, engagement, outcomes, revenue. |

## Commerce

| Method/path | Purpose |
| --- | --- |
| `POST /checkout/quote` | Validate course selection and coupon; returns authoritative totals. |
| `POST /checkout/session` | Creates idempotent pending order and payment-provider checkout session. |
| `GET /orders` / `GET /orders/:id` | Customer order history/detail. |
| `POST /webhooks/stripe` | Raw-body verified Stripe event endpoint; no user session. |

## Administration

| Method/path | Purpose |
| --- | --- |
| `GET /admin/users` / `PATCH /admin/users/:id` | Search users; suspend/reactivate, manage roles. |
| `GET /admin/courses` / `POST /admin/courses/:id/publish` | Review and publish/archive content. |
| `POST/PATCH /admin/coupons` | Coupon lifecycle management. |
| `GET /admin/orders` / `POST /admin/payments/:id/refund` | Support and refund operations with audit reason. |
| `GET /admin/reviews` / `PATCH /admin/reviews/:id` | Review moderation. |
| `GET /admin/analytics/overview` | Platform-level metrics and exports. |
| `GET /admin/audit-logs` | Filtered immutable audit log access. |

## Example: progress update

```http
PUT /api/v1/lessons/0d4.../progress
Idempotency-Key: 53a...
Content-Type: application/json

{"progressPercent": 70, "lastPositionSeconds": 352}
```

The response returns the calculated lesson status and current course progress. The server rejects progress for an unenrolled user, values out of range, and impossible video-position jumps according to a configurable tolerance.
