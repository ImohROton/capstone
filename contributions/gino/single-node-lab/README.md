# Capstone: Gino's single-node gateway and monitoring handoff

**Owner:** Gino Hernandez, Group#3. Updated October 22, 2026 (America/New_York).

This is a sanitized review copy of the supplied Docker lab, not the complete hospital deployment. It contains one DB-less Kong gateway, a synthetic Flask API, its PostgreSQL database, Keycloak in development mode, Prometheus, and Grafana. It is intended for local student testing only.

## Status as of October 22, 2026

This folder records Gino's single-node contribution. It is separate from Imoh's three-node implementation in the repository root. Run commands from this folder only when intentionally running this historical lab.

- Gino ran the revised lab on Windows Docker Desktop on October 21–22. Missing, expired and modified-signature tokens produced 401 responses; a valid doctor request produced 200. Screenshots are in Gino's separate Google Doc report.
- The added `itadmin1` consumer was denied with 403 by the static Kong ACL. The matching request ID is in `evidence/TC-NEG-02-403-kong-log.txt`. Gino also reported doctor access remained 200 after this change.
- A controlled same-node, same-consumer minute window produced ten 200 responses followed by two 429 responses. All twelve response headers and timestamped results are included.
- Grafana displayed 401, 403 and 429 counters. This Classic JSON export contains all three panels and the corrected description. Importing this exact final export on another machine remains to be checked.
- Realm initialization is a manual dependency. No private realm export, database backup, actual `.env`, or user/client credentials are included.
- No multi-node, firewall, internal service isolation, key-rotation, or production-readiness result is claimed by this contribution.
- Package review checked YAML/JSON parsing, Python syntax, query/data-source alignment and saved HTTP statuses. It did not rerun Docker or security tests.

See `docs/validation.md` for evidence scope and `docs/reproduction.md` for test procedures. Configuration export is not a backup of Keycloak users or Prometheus history.

## Changes from the supplied files

1. Removed hard-coded database and Keycloak admin passwords; added a Grafana bootstrap password setting. `.env.example` contains empty values, with Compose requiring real local values.
2. Published ports bind to `127.0.0.1`. Containers can still communicate on the Compose network. Kong's internal Admin listener stays reachable by Prometheus.
3. API connection uses separate PG environment variables instead of embedding credentials in a URL; the HTTP routes and synthetic records are unchanged.
4. Added a PostgreSQL health check and made API startup wait for it. This is startup ordering, not ongoing database failover.
5. Provisioned the Prometheus data source with the same UID referenced by the exported dashboard. Set dashboard refresh to five seconds; retained its cumulative-counter queries. Removed export-instance metadata. The dashboard itself is imported manually.
6. Named the Compose project `capstone-handoff` and removed fixed container names. Its new volumes do not reuse the original `capstone` volumes.
7. Retained the public RSA key and doctor1 and itadmin1 subject identifiers as a lab reference. They are not private keys or passwords. The `secret` field is an explicitly dummy value for RS256.

## First run on Windows

Use a separate extracted folder. Do not overwrite the original working project.

1. If the original lab is running, open PowerShell in the original `capstone` folder and run `docker compose stop` to release ports. Do not delete its volumes.
2. Open PowerShell in `contributions/gino/single-node-lab`. The Compose project name is still `capstone-handoff`; it can address the existing handoff containers/volumes on the same PC. Do not run two copies of that project simultaneously.
3. Run `Copy-Item .env.example .env` only if `.env` does not already exist. Open `.env` locally and fill in three different strong passwords. Long random hexadecimal values avoid quoting and Compose interpolation surprises. Do not paste or commit the filled file.
4. Run `docker compose config --quiet`. This validates the configuration without printing resolved credentials.
5. Run `docker compose up -d --build`, then `docker compose ps`. Check logs for startup errors.

Local endpoints:

| Component | URL |
|---|---|
| Kong proxy | http://localhost:8000/api/patients |
| Kong Admin API | http://localhost:8001 |
| Keycloak | http://localhost:8080 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

API and PostgreSQL have no published host ports. This does not prevent other containers on the shared network from contacting them.

## Identity setup: coordinate with Imoh

On fresh volumes, Compose starts Keycloak but does not import the healthcare realm. Use Imoh's approved realm import procedure, then confirm the healthcare realm, client configuration, and both doctor1 and itadmin1 test identities. Bootstrap admin credentials come from `.env` on first initialization; changing the file does not necessarily reset an existing administrator or database password.

Before token tests, match `kong/kong.yml` to the active realm:

- JWT `key` must match the test user's `sub` claim because `key_claim_name` is `sub`.
- `rsa_public_key` must match the active Keycloak signing key. Realm import or a new realm instance can change the key material.
- Keep RS256 verification and `claims_to_verify: [exp]` enabled. Do not bypass signature checks to make imports work.
- After editing the declarative file, run `docker compose restart kong`.

Keep exports with credentials/private keys out of Git. The route allows the static `doctor` ACL group. `doctor1` belongs to `doctor`; `itadmin1` belongs to `it-admin` and is denied. This is not automatic Keycloak role enforcement. There are no separate GET/POST permissions. The JWT configuration does not establish issuer or audience validation.

## Grafana setup

1. Sign into Grafana with username `admin` and the password set in `.env`.
2. Confirm the provisioned `prometheus` data source connects to `http://prometheus:9090`.
3. Use Grafana's dashboard import workflow to import `grafana/dashboards/gateway-security.json`. The supplied export uses the Classic dashboard JSON model, exported from Gino's Grafana 13.2.3 environment. Re-import of this final export remains untested. Panels reference data-source UID `eg1cylggcan7kc`, matching the included provisioning file.
4. In Prometheus, confirm the `kong` target is UP. Generate fresh requests, then inspect the 401, 403 and 429 panels.

Empty graphs before matching requests are not evidence of a denial. The JSON contains configuration, not historical metrics. The panels show cumulative counters, not counts within the selected time window. All three status panels are included; no automatic alert rule is included. Counters reset when Kong restarts. The queries sum matching series and do not distinguish gateway nodes.

## Validation and remaining limits

See `docs/validation.md`. Repeat the checks after realm/key changes or integration into the three-node environment. Historical single-node results do not certify the integrated deployment. Current image tags include `latest` for Prometheus/Grafana and moving minor tags elsewhere. Record resolved image versions/digests after validation before freezing the final demonstration.

The mock API does not validate JWTs. Direct network access to it bypasses Kong. Its `/health` endpoint reports process health without querying the database. Flask runs its development server. Keycloak uses development storage; the PostgreSQL service here belongs to the mock clinical API, not Keycloak. All services share the default Compose network. There is no TLS, VPN, campus VLAN enforcement, cloud load balancer, gateway redundancy, key rotation test, or production compliance validation in this package.

## GitHub contribution

Add this content on a separate review branch after collaborator access is granted. Compare with the current repository before copying files. Never use a blanket upload of the original project folder. Review staged changes for `.env`, realm exports, backups, tokens and raw logs. `.gitignore` does not remove files already tracked by Git. Do not merge until the team has reviewed and tested the package.

## References

- https://docs.docker.com/compose/how-tos/startup-order/
- https://grafana.com/docs/grafana/latest/administration/provisioning/
- https://developer.konghq.com/plugins/jwt/

## Integration into the shared three-node project

This subfolder is a record and runnable lab reference, not a replacement for the root Compose configuration. Compare and port the two consumers, JWT public-key/subject mappings, ACL rules and rate-limit settings as needed. Verify Prometheus target names, `job` and `route` labels, and data-source UID before importing the dashboard. Add per-instance visibility for node testing. Local counters are independent per gateway; a 10/minute per-node limit is not a shared 10/minute cluster quota. Preserve existing Keycloak data and agree on the realm/user IDs and signing key before combining configurations.

Screenshots remain in Gino's Google Doc report; its link and PDF are not included in this ZIP. No automated test suite was supplied. The reproduction guide documents manual checks rather than claiming new executions.
