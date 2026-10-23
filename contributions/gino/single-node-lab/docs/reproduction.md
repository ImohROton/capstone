# Manual reproduction guide

These are instructions for a future run, not additional executed results. Use only synthetic test accounts/data. Run in this lab folder after the README setup. Preserve timestamp, configuration revision, request ID, expected/actual result and relevant log for each test. Keep credentials and bearer tokens out of shared output.

## Prerequisites

1. Coordinate with Imoh to import/create healthcare, the healthcare-api client, doctor1 and itadmin1. Client authentication and Direct Access Grants were used for this local password-grant demo. This is not a recommended production login flow.
2. Set non-temporary passwords and complete required user profile/actions. Obtain client credentials privately.
3. Match both Kong consumer JWT keys to their actual user `sub` identifiers and use the active realm's RSA public key. Preserve RS256 and expiration verification. Keep doctor1 in doctor and itadmin1 in it-admin; allow only doctor on demo-route.
4. Validate with `docker compose exec kong kong config parse /kong/declarative/kong.yml`, restart Kong and check its status. Account for reset counters.
5. Obtain fresh short-lived tokens through Imoh's token procedure. A setup/token-endpoint failure is not a passed gateway denial. Token lifetime was 300 seconds in the observed run. Do not paste tokens into reports.

## Test sequence and acceptance criteria

1. Positive control: send GET http://localhost:8000/api/patients with the fresh doctor bearer token. Expect 200 and synthetic records.
2. Missing token: `curl.exe -sS -i http://localhost:8000/api/patients`. Expect 401.
3. Tampered signature: create a copy of a valid token and change a character in its signature segment only. Request with that copy while the original remains unexpired. Expect 401 with signature rejection; confirm the original still returns 200, accounting for the rate limit.
4. Expired token: preserve an unmodified doctor token that returned 200. Wait until its exp timestamp has passed, then request with the same token. Expect 401 with expiration rejection. Record token times without publishing the token.
5. ACL: obtain a fresh itadmin1 token and request the same endpoint. Expect 403 and the ACL denial message. Obtain a fresh doctor token and confirm 200. Match the denial response request ID to the Kong log. This validates static consumer ACLs, not dynamic realm-role mapping.
6. Rate limit: obtain a fresh doctor token; wait for a clean minute boundary and start shortly afterward. Send twelve requests to the same node using that token with no other requests for that consumer. Finish within the minute and before token expiry. Expect ten 200s followed by two 429s. Capture response headers and timestamped outcomes. If the window changes, a token expires or other requests consume quota, mark the run inconclusive and repeat under controlled conditions.
7. Monitoring: confirm `up{job="kong"}` is 1 in Prometheus. Record baseline counters, generate denials and compare subsequent scrapes. Grafana refresh and scrape intervals are configured at 5s; this is not a measured 5-second delivery guarantee. Capture separate report screenshots with the relevant time range.

The dashboard queries are `sum(kong_http_requests_total{job="kong",route="demo-route",code="401"})` and the equivalent 403/429 expressions. Run PromQL in Prometheus or Grafana, not PowerShell. These are cumulative totals, not selected-window event counts.

## Three-node follow-up

Review the root implementation before applying this configuration. Test each gateway's controls individually, then through the load balancer. Identify which node handled each request and distinguish independent local quotas from a cluster-wide quota. Define a failover target before testing; record failure time, request outcomes and recovery time under a traffic rate that will not trigger rate limiting. Confirm denials remain enforced with a node unavailable. Multiple containers on one PC do not prove resilience to PC failure or Azure availability-zone loss.
