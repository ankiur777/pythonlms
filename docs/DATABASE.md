# Database Schema

PostgreSQL 16 is the system of record. Every future domain table has `id UUID PRIMARY KEY`, `created_at TIMESTAMPTZ NOT NULL`, and `updated_at TIMESTAMPTZ NOT NULL` unless noted. Money is stored as integer minor units plus ISO-4217 `currency`; timestamps are UTC. Django migrations own schema changes.

## Identity and authorization

| Table | Core columns | Notes |
| --- | --- | --- |
| `users` | `email` (unique, citext), `password_hash`, `status`, `email_verified_at`, `last_login_at` | Status: active, suspended, deleted. Soft-delete PII under retention policy. |
| `user_profiles` | `user_id` (unique FK), `display_name`, `avatar_key`, `bio`, `locale`, `timezone` | Public fields are separately consented. |
| `roles` / `user_roles` | `name` / `user_id`, `role_id` | Seeded student, instructor, admin, support roles. |
| `sessions` | `user_id`, `token_hash` (unique), `expires_at`, `revoked_at`, `ip_hash`, `user_agent` | Refresh-session rotation and forced logout. |
| `password_reset_tokens` | `user_id`, `token_hash`, `expires_at`, `used_at` | One-time, short-lived. |
| `audit_logs` | `actor_user_id`, `action`, `entity_type`, `entity_id`, `metadata`, `ip_hash` | Append-only; no secrets or raw tokens. |

## Catalog and content

| Table | Core columns | Notes |
| --- | --- | --- |
| `categories` | `name`, `slug` (unique), `parent_id` | Hierarchical catalog taxonomy. |
| `courses` | `slug` (unique), `title`, `summary`, `description`, `level`, `language`, `status`, `thumbnail_key`, `completion_rule` | Status: draft, review, published, archived. |
| `course_instructors` | `course_id`, `user_id`, `role` | Unique (`course_id`, `user_id`); owner/editor/reviewer. |
| `course_categories` | `course_id`, `category_id` | Many-to-many. |
| `course_prices` | `course_id`, `amount_minor`, `currency`, `active_from`, `active_to` | Historical, immutable prices. |
| `modules` | `course_id`, `title`, `position`, `is_published` | Unique (`course_id`, `position`). |
| `lessons` | `module_id`, `type`, `title`, `position`, `is_preview`, `status`, `estimated_minutes`, `content_version` | Type: video, text, code, quiz, assignment, project. |
| `lesson_contents` | `lesson_id` (unique), `body_json`, `video_asset_id`, `starter_code`, `runner_config`, `settings_json` | Type-specific data; revision history in `lesson_revisions`. |
| `lesson_revisions` | `lesson_id`, `version`, `content_json`, `author_id`, `published_at` | Immutable snapshot for reproducibility. |
| `assets` | `storage_key` (unique), `kind`, `mime_type`, `size_bytes`, `checksum`, `owner_id` | Object metadata only; private by default. |

## Learning and assessment

| Table | Core columns | Notes |
| --- | --- | --- |
| `enrollments` | `user_id`, `course_id`, `source`, `status`, `started_at`, `completed_at`, `expires_at` | Unique active enrollment per user/course; source order/admin/grant. |
| `lesson_progress` | `enrollment_id`, `lesson_id`, `status`, `progress_percent`, `last_position_seconds`, `completed_at` | Unique (`enrollment_id`, `lesson_id`); server-calculated boundaries. |
| `progress_events` | `enrollment_id`, `lesson_id`, `event_type`, `idempotency_key`, `payload`, `occurred_at` | Partition monthly; unique idempotency key. |
| `quiz_questions` | `lesson_id`, `type`, `prompt_json`, `position`, `points`, `required` | Answers are never returned to learners. |
| `quiz_options` | `question_id`, `body`, `is_correct`, `position` | `is_correct` protected in server query layer. |
| `quiz_attempts` | `enrollment_id`, `lesson_id`, `attempt_no`, `status`, `score`, `started_at`, `submitted_at` | Unique (`enrollment_id`, `lesson_id`, `attempt_no`). |
| `quiz_responses` | `attempt_id`, `question_id`, `answer_json`, `is_correct`, `points_awarded` | Snapshot grading outcome. |
| `submissions` | `enrollment_id`, `lesson_id`, `attempt_no`, `kind`, `content_json`, `status`, `submitted_at` | Assignment/project/code submissions. |
| `submission_runs` | `submission_id`, `status`, `runner_image`, `stdout_key`, `stderr_key`, `result_json`, `started_at`, `finished_at` | Never persist executable secrets. |
| `grades` | `submission_id` (unique), `grader_id`, `score`, `feedback`, `rubric_json`, `graded_at` | Manual or automated grade provenance. |
| `certificates` | `enrollment_id` (unique), `verification_code` (unique), `issued_at`, `pdf_key`, `revoked_at` | Public URL uses random non-sequential code. |

## Commerce and engagement

| Table | Core columns | Notes |
| --- | --- | --- |
| `coupons` | `code` (unique), `type`, `value`, `currency`, `max_redemptions`, `starts_at`, `ends_at`, `active` | Percentage or fixed discount; scope via join table. |
| `coupon_courses` / `coupon_redemptions` | coupon/course / coupon/user/order | Unique redemption constraints prevent double use. |
| `orders` | `user_id`, `status`, `subtotal_minor`, `discount_minor`, `tax_minor`, `total_minor`, `currency`, `idempotency_key` | Immutable totals and snapshot line data. |
| `order_items` | `order_id`, `course_id`, `title_snapshot`, `unit_amount_minor`, `discount_minor` | Unique (`order_id`, `course_id`). |
| `payments` | `order_id`, `provider`, `provider_payment_id` (unique), `status`, `amount_minor`, `paid_at`, `raw_event_key` | Provider payload encrypted/object-stored with retention. |
| `refunds` | `payment_id`, `provider_refund_id` (unique), `amount_minor`, `status`, `reason` | Refund worker may revoke entitlement per policy. |
| `reviews` | `course_id`, `user_id`, `rating`, `body`, `status` | Unique (`course_id`, `user_id`); only enrolled users can create. |
| `notifications` | `user_id`, `type`, `channel`, `payload`, `read_at`, `sent_at`, `failed_at` | Queue-backed delivery; payload is minimal. |
| `search_documents` | `entity_type`, `entity_id`, `text`, `updated_at` | Adapter source for external search index. |
| `daily_course_metrics` | `course_id`, `metric_date`, `views`, `enrollments`, `completions`, `revenue_minor` | Unique (`course_id`, `metric_date`). |
| `outbox_events` | `type`, `aggregate_type`, `aggregate_id`, `payload`, `available_at`, `processed_at` | Transactional event publishing. |

## Constraints and indexes

- Foreign keys use `RESTRICT` for financial/content history and `CASCADE` only for clearly owned ephemeral records.
- Composite indexes: `enrollments(user_id, status)`, `modules(course_id, position)`, `lessons(module_id, position)`, `lesson_progress(enrollment_id, status)`, `orders(user_id, created_at DESC)`, `notifications(user_id, read_at, created_at DESC)`.
- GIN full-text index on published course title/summary/description. Add trigram indexes for autocomplete.
- Use `SELECT ... FOR UPDATE` on coupon redemption and payment fulfillment. The webhook event ID has a unique constraint.
- Row-level security is optional defense-in-depth; application-scoped DB credentials and policy tests remain mandatory.
