# Validation record — Gino Hernandez, Group #3

Scope: single-node Windows Docker lab, October 21–22, 2026. Local timestamps use America/New_York (EDT, UTC-4); Kong log timestamps use UTC. The evidence predates this documentation update. It does not validate Imoh's three-node setup.

| Check | Acceptance criterion | Observed status and evidence |
|---|---|---|
| Startup / identity | Services running; healthcare realm reachable; usable token obtained | Observed during guided session; fresh-machine setup remains untested |
| Allowed doctor | Valid allowed token returns 200 for GET /api/patients | Observed 23:36:45 EDT Oct 21; API log request ID 73ebcf292dc15c31f2377d58713cea54. Doctor 200 after ACL change reported by Gino |
| Missing token, TC-NEG-01 | Missing Authorization token returns 401 | Observed in session; screenshot in separate report, not this ZIP |
| Expired token, TC-NEG-01 | Expired token rejected with 401 and expiration reason | 23:36:05 EDT Oct 21, request ID e5c2a4473658da4717455f6e40761108; 401 log included, reason shown in separate response screenshot. Strict same-token before/after sequence not established by packaged logs alone |
| Tampered signature, TC-NEG-01 | Modify signature of an otherwise valid JWT; reject with 401 | 23:40:41 EDT Oct 21, request ID 7de46d4c7435de616bd1a261e4e5fb01; 401 log included; invalid-signature response screenshot in report |
| Static ACL, TC-NEG-02 | Valid recognized itadmin1 denied 403 while doctor remains allowed | 00:37:23 EDT Oct 22, request ID dd15eb0a6a8d2562cb742c1714bd0f16; matching log included. Does not establish dynamic Keycloak RBAC |
| Local rate limit, TC-NEG-03 | Same consumer/node, clean fixed minute: requests 1–10 = 200; 11–12 = 429 | Passed recorded run, 23:47:05–23:47:24 EDT Oct 21. results.txt plus all twelve headers and logs included |
| Status visibility, TC-NEG-06 | Generated 401/403/429 denials visible in matching Grafana panels | Observed in session screenshots; corrected 403 panel displayed 1. Final JSON contains all three queries. No measured end-to-end display-latency bound or alert delivery test |
| Internal service denial, TC-NEG-04 | Unauthorized service call rejected at specified enforcement point | Pending; API itself does not authenticate direct calls |
| Cross-zone PostgreSQL denial, TC-NEG-05 | VLAN 60 to VLAN 80 TCP 5432 denied and logged by firewall | Not implemented in this shared-network Docker lab |
| Multi-node rate/failover | Agree threshold, test each node, measure failed requests and sustained recovery | Pending integration/testing of Imoh's implementation |

## Evidence files

- `evidence/TC-NEG-02-403-kong-log.txt`: matching 403 access-log event.
- `evidence/rate-limit-20261021-234636/results.txt`: twelve timestamped outcomes.
- `request-1.headers.txt` through `request-12.headers.txt` in that folder: actual response headers.
- `kong-api-only.txt`: filtered API access records, including earlier authentication tests.
- `kong-test-logs.txt`: broader Kong log excerpt, including metric scrapes.

Evidence bytes were preserved. Some PowerShell text files use UTF-16; this is normal and not corrupt data. Logs record status and request ID, not the JWT-validation reason or authenticated user. Correlate with the separate report's request setup and response screenshots.

Kong restarted around 00:30 EDT Oct 22. The recorded 401/429 results precede the restart; the 403 result follows it. A flat cumulative value of 1 means one recorded event, not repeated denials. Dashboard JSON contains queries/layout only, not historical metrics.

## Limits

Synthetic patients only. No TLS, real Azure deployment, availability-zone isolation, VPN, FortiGate enforcement, Keycloak PostgreSQL cluster, key rotation, audit retention or healthcare compliance certification was demonstrated. Keycloak uses development storage; PostgreSQL serves the mock API. All containers share a network. Grafana is a visualization tool and Prometheus stores numerical metrics, not access logs.
