# Production Deployment

## Environments

Use isolated `development`, `staging`, and `production` accounts/projects. Production is deployed only from protected, reviewed commits. Staging uses separate payment test keys, storage buckets, database, and email domain.

## Container topology

- `web`: React static build served by Nginx behind CDN/WAF and load balancer.
- `api`: stateless Django/DRF Gunicorn containers behind the same private load balancer route.
- `worker`: independently scaled Celery worker containers.
- `code-runner`: separate restricted cluster/node pool, never co-located with API.
- Managed PostgreSQL, managed Redis, S3-compatible storage/CDN, managed queue/email/video providers.

The recommended initial target is AWS: CloudFront + WAF, ECS Fargate (or EKS), RDS PostgreSQL Multi-AZ, ElastiCache Redis, S3, Secrets Manager, and CloudWatch/OpenTelemetry collector. Terraform defines all infrastructure. Equivalent managed services on GCP/Azure are acceptable through provider adapters.

## CI/CD

1. Pull request: formatting, typecheck, unit tests, API contract tests, migrations validation, SAST, dependency/secret scanning, container/IaC scan.
2. Main branch: build immutable images tagged with Git SHA, generate SBOM, sign image, deploy to staging, run migrations and E2E smoke tests.
3. Production: protected approval, backup verification, expand-only migration, canary/rolling deploy, health checks, automated rollback on SLO/error threshold breach.

Migrations run as a dedicated one-shot job before application rollout. Destructive schema changes follow expand → backfill → dual-read/write → contract across releases. Never run ad hoc production schema changes.

## Configuration

Environment schema validation must fail startup for missing/malformed variables. Required secrets include database/Redis URLs, session signing keys, encryption/KMS configuration, Stripe secret/webhook secret, email provider credentials, storage configuration, video provider credentials, Sentry DSN, and OpenTelemetry exporter endpoint. `.env.example` contains names only, never values.

## Reliability and operations

- Liveness/readiness endpoints: `/health/live`, `/health/ready`; readiness confirms dependency connectivity without exposing configuration.
- Nightly encrypted database backups with point-in-time recovery; object versioning and lifecycle retention; quarterly restore drills.
- Autoscale web/API by CPU, memory, and request latency; workers by queue depth; independently cap code-runner concurrency.
- Alerts: 5xx rate, latency, saturation, queue age/failures, database capacity, backup failure, payment webhook failures, suspicious auth activity.
- Apply CDN caching for public catalog pages; never cache authenticated/private API responses at shared layers.

## Go-live checklist

- Domain, TLS, CSP, WAF, DNS, transactional email records, and status page configured.
- Payment webhook configured with production signing secret and replay tests passed.
- Monitoring dashboards, on-call ownership, runbooks, incident contacts, and backup restore evidence complete.
- Accessibility, performance, security, privacy, and cross-browser E2E acceptance criteria passed.
