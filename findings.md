# Fleet Ops — Bug Findings

**Date:** 2026-05-20  
**Scope:** booking-service, loyalty-service, fleet-service, notifications-service, index.html, mcp/fleet-status, mcp/guest-contacts  
**Bugs found:** 30 | **Test failures:** 3 confirmed (loyalty: 1, fleet: 1, notifications: 1)

---

## Summary

| #   | Service       | Severity   | Title                                                                            |
| --- | ------------- | ---------- | -------------------------------------------------------------------------------- |
| 1   | loyalty       | **High**   | Gold tier threshold: `> 5000` should be `>= 5000` — test failure                 |
| 2   | fleet         | **High**   | `limit` param ignored in `get_available_cabins` — test failure                   |
| 3   | notifications | **High**   | Opted-in notifications stuck at `pending`, never set to `sent` — test failure    |
| 4   | booking       | **Medium** | `float + Decimal` TypeError on non-interior bookings in SQLite (local dev crash) |
| 5   | booking       | **Medium** | `GET /bookings/guest/{guest_id}` may be shadowed — untested                      |
| 6   | booking       | **Medium** | `BookingStatus.pending` not in schema spec, never written                        |
| 7   | booking       | **Medium** | Guest functions misplaced inside `itinerary_service.py`                          |
| 8   | booking       | **Medium** | Test DB uses on-disk file instead of in-memory SQLite                            |
| 9   | loyalty       | **Medium** | `AwardPointsRequest.amount` allows negatives — silent point drain                |
| 10  | loyalty       | **Medium** | `RedeemPointsRequest.amount` allows negatives — bypasses balance check           |
| 11  | fleet         | **Medium** | `get_available_cabins` does no real availability check — returns all cabins      |
| 12  | fleet         | **Medium** | `departure_date`/`arrival_date` stored as `String` — no date validation          |
| 13  | notifications | **Medium** | `sent_at` never populated for sent notifications                                 |
| 14  | notifications | **Medium** | No way to opt out — `opted_in` missing from `GuestContactCreate` schema          |
| 15  | notifications | **Medium** | `opted_in` silently dropped on contact update                                    |
| 16  | UI            | **Medium** | `guestR.value` accessed without checking `allSettled` fulfillment status         |
| 17  | UI            | **Medium** | `loadDashboard` has no error handling on `fetchAllGuests`                        |
| 18  | MCP           | **Medium** | `get_ship_availability` returns hardcoded cabin counts, ignores live data        |
| 19  | MCP           | **Medium** | `get_cabin_pricing` uses hardcoded rates, ignores live `base_rate_usd`           |
| 20  | MCP           | **Medium** | `guest-contacts` hardcoded dict, not connected to notifications-service          |
| 21  | MCP           | **Medium** | `opted_in` defaults to `True` when field absent — unsafe assumption              |
| 22  | fleet         | **Low**    | `if ship_id:` falsy for `ship_id=0` — should be `if ship_id is not None:`        |
| 23  | loyalty       | **Low**    | `test_silver_threshold` tests no transition — 999→1000 boundary uncovered        |
| 24  | loyalty       | **Low**    | Seed redemption transaction has wrong sign vs. service behavior                  |
| 25  | notifications | **Low**    | `sent_at` timezone inconsistency (naive seed vs. aware runtime)                  |
| 26  | booking       | **Low**    | Dead `list_itineraries` function shadows correct `search_itineraries`            |
| 27  | booking       | **Low**    | Seed `total_price_usd` hardcoded, drifts if pricing formula changes              |
| 28  | UI            | **Low**    | Notification history empty with no explanation when `guestCache` is cold         |
| 29  | MCP           | **Low**    | `SHIPS` dict hardcoded, will diverge from fleet-service DB                       |
| 30  | MCP           | **Low**    | Both MCP servers don't handle `ping` — "Method not found" on keepalive           |

---

## Confirmed Test Failures

### Loyalty — `test_gold_threshold_exact`

`loyalty-service/services/loyalty_service.py:9` — `calculate_tier` uses strict comparison. A guest with exactly 5000 points is classified Silver instead of Gold.

### Fleet — `test_available_cabins_respects_limit`

`fleet-service/services/fleet_service.py:35` — `get_available_cabins` ignores the `limit` parameter. 12 cabins returned when `limit=3`.

### Notifications — `test_send_notification_success`

`notifications-service/services/notification_service.py:62-73` — opted-in branch creates a `Notification` record but never advances its status from `pending`.

---

## Medium Severity Details

### Bug 4: `float + Decimal` crash on non-interior bookings (local dev)

`booking-service/services/booking_service.py:43` — SQLite returns `base_price_usd` as `float`; `CABIN_UPLIFT` values are `Decimal`. `float + Decimal` raises `TypeError` in Python 3. Tests pass only because the test suite uses interior cabins (uplift = `Decimal("0.00")`). Any balcony/suite/ocean_view booking crashes locally. Production (PostgreSQL) returns `Decimal` so it works there.

### Bug 11: `get_available_cabins` does no real availability check

`fleet-service/services/fleet_service.py:25-35` — function returns all cabins for a ship (optionally filtered by category), identical to `get_ship_cabins`. No check against bookings or sailing occupancy. Since booking data lives in a separate service, a cross-service HTTP call to booking-service would be required for true availability.

### Bugs 14-15: No opt-out path in notifications-service

`notifications-service/schemas.py:6-10`, `services/notification_service.py:14-36` — `GuestContactCreate` has no `opted_in` field. All guests created/updated via `POST /contacts` are permanently opted in. Even if the field were added, the update branch only writes `email`, `phone`, `preferred_channel` — `opted_in` would still be silently dropped.

### Bugs 18-21: Both MCP servers use hardcoded data

`mcp/fleet-status/server.py` — ship list, cabin availability counts, and pricing are all static dicts. `mcp/guest-contacts/server.py` — 8-guest hardcoded dict instead of calling `GET /contacts/{guest_id}`. Both servers will diverge from live data immediately.

---

## INC-3104 Verification

The 2024-01-09 suppression logic hotfix is correct. `notification_service.py` line 48: `if not contact.opted_in:` correctly suppresses opted-out guests. `test_send_notification_opted_out_suppressed` passes. The current bug is unrelated — the opted-in path creates records with `status=pending` and never advances them.
