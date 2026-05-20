# Fleet Ops

Multi-service cruise operations platform for NCLH engineering workshops.

## Services

| Service               | Port | Purpose                                           |
| --------------------- | ---- | ------------------------------------------------- |
| booking-service       | 8000 | Itinerary search, cabin selection, confirmations  |
| loyalty-service       | 8001 | Bronze/Silver/Gold tier management, points ledger |
| fleet-service         | 8002 | Ship inventory, cabin catalog, sailing schedules  |
| notifications-service | 8003 | Guest communications (stub)                       |

## Quickstart

Open Claude Code in this directory and ask:

> "Set up all four services using uv and run the tests to confirm everything is working."

## Stack

Python 3.11+, FastAPI, SQLite, uv
