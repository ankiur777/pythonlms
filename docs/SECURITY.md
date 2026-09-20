# Security Design

Security requirements apply from the first implementation increment, not as a hardening pass.

## Identity and sessions

- Hash passwords with Argon2id using current OWASP-recommended parameters; never log credentials or reset links.
- Email verification precedes sensitive actions. Reset and verification tokens are random, hashed at rest, single-use, and expire quickly.
- Issue short-lived access tokens and rotate opaque refresh sessions stored in `Secure`, `HttpOnly`, `SameSite=Lax` cookies. Detect refresh-token reuse and revoke the session family.
- Require MFA for administrators before production launch; provide TOTP/WebAuthn enrollment and recovery codes.
- Apply progressive login throttling by account and IP, generic authentication error messages, CAPTCHA only after suspicious thresholds, and breach-password screening.

## Authorization and data protection

- Enforce RBAC plus resource ownership in API guards/services; test every role/resource pair. Client routes are convenience only.
- Use Django ORM queries, DRF serializer allow-lists, strict content type/size limits, and output encoding. Sanitize rich-text HTML through an allow-list.
- Encrypt traffic with TLS 1.2+; encrypt databases, backups, and object storage with provider KMS keys. Secrets live only in a managed secret store and are rotated.
- Separate production/staging credentials and least-privilege database, storage, CI, and payment-provider roles.
- Minimize PII. Encrypt sensitive provider payloads, define retention/deletion workflows, and support data export/deletion requests consistent with legal obligations.

## Web, API, and media defenses

- Set CSP, HSTS, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`, and frame-ancestors protections. Use CSRF protection for cookie-authenticated mutations.
- Validate webhook signatures against the raw request body; persist event IDs uniquely before processing. Never rely on redirect success pages to grant access.
- Rate-limit authentication, search, uploads, progress, and checkout endpoints using Redis. Cap request body sizes and enforce cursor/page limits.
- Assets are private. Uploads use short-lived presigned URLs with exact MIME/size constraints and asynchronous malware scanning. Playback URLs are short-lived, signed, and entitlement-scoped.

## Code-runner isolation

- Use a dedicated, non-privileged runner account and ephemeral Firecracker microVMs or an equivalent hardened sandbox.
- Deny outbound network by default; no host mounts, Docker socket, cloud credentials, or production database access.
- Apply CPU, memory, process, execution-time, and output-size limits; pin read-only images and scan them in CI.
- Treat source, dependencies, stdout, and artifacts as untrusted. Escape output before display and store it separately with retention limits.

## Operational controls

- Structured audit events cover roles, course publishing, grades, refunds, coupons, impersonation, and security settings.
- Centralize logs with PII scrubbing; monitor auth failures, privilege changes, webhook failures, anomalous payments, and runner escapes.
- Run SAST, dependency/SBOM, secret, container, IaC, DAST, and authorization tests in CI. Patch critical vulnerabilities under an explicit SLA.
- Backups are encrypted and restore-tested quarterly. Maintain incident response, key rotation, access review, and disaster-recovery runbooks.
