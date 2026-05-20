# Fleet Ops — Developer Guide

**Last updated:** September 2024 (do not edit, see Confluence for latest)

---

## Overview

Fleet Ops is NCLH's internal cruise operations platform, originally built on Tornado (async Python web framework) and migrated to FastAPI in Q3 2023. The core services handle guest booking, loyalty tier management, fleet inventory, and guest communications. This document is the canonical developer reference for all four services.

---

## Team

Current owners and contacts. Ping these people for access, questions, or incidents.

| Service               | Owner         | GitHub      | Slack         |
| --------------------- | ------------- | ----------- | ------------- |
| booking-service       | Dmitri Volkov | @dmitriv    | #eng-booking  |
| loyalty-service       | Anya Patel    | @anyap      | #eng-loyalty  |
| fleet-service         | Marcus Webb   | @mwebb      | #eng-fleet    |
| notifications-service | Keisha Monroe | @kmonroe    | #eng-notifs   |
| Infrastructure        | Todd Larsen   | @tlarsen    | #eng-infra    |
| Platform (MCP)        | Yuki Tanaka   | @yukitanaka | #eng-platform |

Former owners (no longer at company, kept for git blame reference):

- booking-service (2021-2022): Brian Holloway @bholloway
- loyalty-service (2020-2023): Rachel Fong @rfong
- fleet-service (2019-2022): Nnamdi Achebe @nachebe
- notifications-service (2021): Tyler Pruitt @tpruitt
- DB migrations (all): Luis Carrasco @lcarrasco

---

## Architecture

```
booking-service  ──┐
loyalty-service  ──┼──  PostgreSQL (prod) / SQLite (local dev)
fleet-service    ──┤
notifications    ──┘
       │
       ├── mcp/fleet-status/     (MCP server, internal tools)
       └── mcp/guest-contacts/   (MCP server, guest data)
```

Each service is a standalone FastAPI app with its own database. In production they share a PostgreSQL cluster; locally each service uses its own SQLite file. Cross-service communication is HTTP only (no shared DB access).

---

## Database Schema

### booking-service (PostgreSQL schema: `booking`)

```sql
CREATE TABLE guests (
    id          SERIAL PRIMARY KEY,
    first_name  VARCHAR(100) NOT NULL,
    last_name   VARCHAR(100) NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    phone       VARCHAR(50),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- NOTE: cabin table was renamed from "staterooms" in migration 0047 (Jan 2023)
CREATE TABLE cabins (
    id              SERIAL PRIMARY KEY,
    cabin_number    VARCHAR(20) NOT NULL,
    category        cabin_category_enum NOT NULL,  -- interior|ocean_view|balcony|suite
    deck            INTEGER NOT NULL,
    max_occupancy   INTEGER NOT NULL DEFAULT 2,
    ship_id         INTEGER REFERENCES ships(id)   -- added migration 0051, may be NULL for legacy rows
);

CREATE TABLE itineraries (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    destination     VARCHAR(100) NOT NULL,
    duration_nights INTEGER NOT NULL,
    departure_port  VARCHAR(100) NOT NULL,
    ship_name       VARCHAR(100) NOT NULL,
    base_price_usd  NUMERIC(10,2) NOT NULL,
    -- deprecated: region_code was used by old Tornado routing, now unused
    region_code     VARCHAR(10)
);

CREATE TABLE bookings (
    id              SERIAL PRIMARY KEY,
    guest_id        INTEGER NOT NULL REFERENCES guests(id),
    itinerary_id    INTEGER NOT NULL REFERENCES itineraries(id),
    cabin_id        INTEGER NOT NULL REFERENCES cabins(id),
    sail_date       DATE NOT NULL,
    status          booking_status_enum NOT NULL DEFAULT 'confirmed',
    total_price_usd NUMERIC(10,2) NOT NULL,
    -- deprecated columns retained for legacy reporting queries:
    agent_code      VARCHAR(20),    -- travel agent code, no longer written
    promo_code      VARCHAR(50),    -- replaced by promotions service (see note)
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### loyalty-service (PostgreSQL schema: `loyalty`)

```sql
CREATE TABLE loyalty_accounts (
    id              SERIAL PRIMARY KEY,
    guest_id        INTEGER UNIQUE NOT NULL,
    guest_email     VARCHAR(255) NOT NULL,
    guest_name      VARCHAR(200) NOT NULL,
    total_points    INTEGER NOT NULL DEFAULT 0,
    tier            loyalty_tier_enum NOT NULL DEFAULT 'Bronze',
    -- NOTE: as of Q2 2023, tier thresholds changed. Old thresholds (Bronze<500, Silver<2000, Gold>=2000)
    -- are WRONG. Current: Bronze<1000, Silver<5000, Gold>=5000
    enrolled_at     TIMESTAMPTZ DEFAULT NOW(),
    last_updated    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE points_transactions (
    id                  SERIAL PRIMARY KEY,
    account_id          INTEGER NOT NULL REFERENCES loyalty_accounts(id),
    amount              INTEGER NOT NULL,
    transaction_type    transaction_type_enum NOT NULL,
    description         VARCHAR(500) NOT NULL,
    -- legacy: booking_ref was used before booking-service had stable IDs
    booking_ref         VARCHAR(50),
    created_at          TIMESTAMPTZ DEFAULT NOW()
);
```

### fleet-service (PostgreSQL schema: `fleet`)

```sql
CREATE TABLE ships (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(200) NOT NULL,
    imo_number          VARCHAR(20) UNIQUE NOT NULL,
    class_name          ship_class_enum NOT NULL,
    total_cabins        INTEGER NOT NULL,
    passenger_capacity  INTEGER NOT NULL,
    home_port           VARCHAR(100) NOT NULL,
    status              ship_status_enum NOT NULL DEFAULT 'active',
    -- deprecated: gross_tonnage was used for port fee calculations, now handled by port-fees-service
    gross_tonnage       INTEGER
);

CREATE TABLE cabins (
    id              SERIAL PRIMARY KEY,
    ship_id         INTEGER NOT NULL REFERENCES ships(id),
    cabin_number    VARCHAR(20) NOT NULL,
    category        cabin_category_enum NOT NULL,
    deck            INTEGER NOT NULL,
    max_occupancy   INTEGER NOT NULL DEFAULT 2,
    base_rate_usd   NUMERIC(10,2) NOT NULL
);

CREATE TABLE sailings (
    id                  SERIAL PRIMARY KEY,
    ship_id             INTEGER NOT NULL REFERENCES ships(id),
    departure_date      DATE NOT NULL,
    arrival_date        DATE NOT NULL,
    departure_port      VARCHAR(100) NOT NULL,
    arrival_port        VARCHAR(100) NOT NULL,
    itinerary_name      VARCHAR(255) NOT NULL,
    -- deprecated: voyage_number format changed in 2022, old format was NCL-MMYY-NNN
    voyage_number       VARCHAR(50)
);
```

---

## API Reference

### booking-service (default port: 8000)

#### POST /guests/

Create a new guest profile.

Request:

```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com",
  "phone": "305-555-0100"
}
```

Response: `201 Created`

```json
{
  "id": 1,
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com",
  "phone": "305-555-0100",
  "created_at": "..."
}
```

#### GET /guests/{guest_id}

Get guest by ID. Returns `404` if not found.

#### GET /itineraries/

List itineraries. Optional query params: `destination`, `min_nights`, `max_nights`.

#### GET /itineraries/{itinerary_id}

Get itinerary by ID.

#### POST /bookings/

Create a booking. Checks cabin availability for the sail_date; returns `409` if already booked.

Request:

```json
{ "guest_id": 1, "itinerary_id": 2, "cabin_id": 3, "sail_date": "2026-06-14" }
```

Pricing: `base_price + cabin_uplift`. Uplifts: interior=+$0, ocean_view=+$150, balcony=+$300, suite=+$750.

#### GET /bookings/{booking_id}

Get booking by ID.

#### DELETE /bookings/{booking_id}

Cancel a booking (sets status to `cancelled`).

#### GET /bookings/guest/{guest_id}

List all active (non-cancelled) bookings for a guest.

---

### loyalty-service (default port: 8001)

#### GET /accounts/{guest_id}

Get loyalty account by guest_id. Returns `404` if no account exists.

#### POST /accounts/{guest_id}/award

Award points to an account. Recalculates tier.

Request: `{"amount": 500, "transaction_type": "booking_credit", "description": "Caribbean sailing"}`

#### POST /accounts/{guest_id}/redeem

Redeem points. Returns `400` if insufficient balance.

Request: `{"amount": 200, "description": "Onboard credit"}`

#### GET /accounts/{guest_id}/transactions

Transaction history. Optional `limit` param (default 50).

---

### fleet-service (default port: 8002)

#### GET /ships/

List ships. Optional `status` filter (`active`, `drydock`, `retired`).

#### GET /ships/{ship_id}

Get ship by ID.

#### GET /ships/{ship_id}/cabins

All cabins for a ship.

#### GET /ships/{ship_id}/cabins/available

Available cabins. Optional `category` and `limit` params.

#### GET /sailings/

List sailings. Optional `ship_id` and `from_date` filters.

#### GET /sailings/{sailing_id}

Get sailing by ID.

---

### notifications-service (default port: 8003)

#### POST /contacts

Create or update a guest contact record.

#### GET /contacts/{guest_id}

Get contact by guest_id.

#### GET /contacts/{guest_id}/history

Notification history for a guest.

#### POST /notify

Send a notification. Suppresses if guest is not opted in.

Request: `{"guest_id": 1, "notification_type": "booking_confirmation", "subject": "...", "body": "..."}`

---

## Setup — Local Development

### Prerequisites

- Python 3.11+
- uv (`pip install uv`)

### Initial setup (from repo root)

```bash
bash setup.sh
```

This installs deps and seeds the database for all four services.

### Starting services

```bash
cd booking-service && uv run uvicorn main:app --reload --port 8000
```

Repeat for each service on its respective port. Each runs independently in a separate terminal.

### Serving the UI dashboard

The Fleet Ops dashboard (`index.html`) is a static file served from the repo root on port 5000:

```bash
python -m http.server 5000
```

Then open http://localhost:5000.

### Running tests

```bash
# From repo root (all services):
bash run_tests.sh

# Single service:
cd <service-directory>
uv run pytest
```

---

## Deployment

**Note: This section describes the legacy Tornado deployment process. FastAPI services use a different process — see the internal Confluence page "FastAPI Deployment Runbook" (link in #eng-infra pinned messages).**

### Legacy Tornado deployment (no longer applicable)

```bash
# This is the OLD process. Do not use.
pip install tornado==6.1 motor==2.5.1
python -m tornado.autoreload app.py --port=8000

# Old supervisor config (deprecated):
# /etc/supervisor/conf.d/fleet-ops.conf
# [program:fleet-ops-booking]
# command=python /srv/fleet-ops/booking/app.py
# directory=/srv/fleet-ops/booking
# autostart=true
# autorestart=true
```

### Docker (current)

```bash
docker build -t fleet-ops-booking ./booking-service
docker run -p 8000:8000 fleet-ops-booking
```

See `docker-compose.yml` in the infra repo (fleet-ops-infra, separate repository).

---

## Code Style Guide — Tornado Era (DEPRECATED)

**This section describes the Tornado-era code style. The project uses FastAPI now. Ignore this section.**

In the original Tornado implementation, all handlers extended `BaseHandler`:

```python
class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

class BookingHandler(BaseHandler):
    async def get(self, booking_id):
        booking = await self.db.bookings.find_one({"_id": ObjectId(booking_id)})
        self.write(json_encode(booking))
```

The MongoDB query patterns used in Tornado are completely different from SQLAlchemy. Do not reference them for new code.

Handler registration (Tornado, deprecated):

```python
app = tornado.web.Application([
    (r"/bookings/(\w+)", BookingHandler),
    (r"/itineraries", ItineraryListHandler),
    (r"/guests/(\w+)", GuestHandler),
])
```

Old environment variables (Tornado era, no longer used):

- `MONGO_URI` — MongoDB connection string
- `TORNADO_PORT` — HTTP port
- `TORNADO_WORKERS` — number of worker processes
- `REDIS_URL` — session cache
- `LEGACY_BOOKING_API_KEY` — integration with old reservations system (decommissioned 2022)

---

## Incident History

Notable incidents for context (full postmortems in PagerDuty):

- **2023-08-14**: Loyalty tier calculation returned incorrect tiers for ~200 guests due to a bad migration that reset `total_points` to 0 for Silver/Gold accounts. Fixed by re-running points recalculation job. Postmortem: INC-2847.
- **2022-11-02**: Booking service OOM under load — unbounded SQLAlchemy query on cabin search returning full table. Added pagination. Postmortem: INC-2201.
- **2024-01-09**: Notification suppression logic inverted — opted-out guests received emails. Hotfix deployed. Postmortem: INC-3104.

---

## MCP Servers

Two MCP servers are included in the `mcp/` directory:

- `mcp/fleet-status/` — ship availability and cabin pricing
- `mcp/guest-contacts/` — guest contact lookup

**Status as of this writing:** Both servers are implemented but not yet connected to Claude Code. Yuki is tracking connection setup in FLEET-892.

To start a server manually:

```bash
python mcp/fleet-status/server.py
```

Connection instructions will be added once FLEET-892 is resolved.

---

## Known Issues / Tech Debt

- [ ] FLEET-744: `get_available_cabins` does not validate that the `limit` parameter is applied consistently across all query paths
- [ ] FLEET-801: Loyalty tier recalculation should be event-driven (currently synchronous on every award call)
- [ ] BOOK-219: Missing index on `bookings.sail_date` — slow for high-volume date range queries
- [ ] NOTIF-88: No retry logic for failed notifications — failed records stay in `failed` status forever
- [ ] BOOK-334: `region_code` column in `itineraries` table still present, never written, should be dropped
- [ ] ALL: No distributed tracing — cross-service request correlation requires manual log correlation

---

## Onboarding Checklist

New engineers joining the Fleet Ops team:

- [ ] Request GitHub access from Todd (@tlarsen)
- [ ] Join Slack channels: #eng-booking, #eng-loyalty, #eng-fleet, #eng-notifs, #eng-infra
- [ ] Set up local dev environment (see Setup section above)
- [ ] Read postmortems INC-2847, INC-2201, INC-3104 (linked above)
- [ ] Pair with service owner for your first PR
- [ ] Get added to PagerDuty rotation for your service (after 30-day ramp)
- [ ] Complete NCLH security training (link in onboarding email)
- [ ] Review NCLH data classification policy — guest PII handling rules apply to this repo
