# Anveshan

**a smarter watch over every login**

Real-time, explainable detection for SIM-swap & account-takeover fraud.

Built for OMNIKON — Theme: Cybersecurity, Blockchain & Digital Trust
Problem Statement: Detecting SIM-Swap and Account-Takeover Fraud

---

## What this is

Most banks only discover SIM-swap fraud *after* the money is gone. SwapShield
scores every login/transaction in real time across multiple behavioral
signals — device change, impossible travel, a recent SIM-change flag,
transaction amount deviation — and explains **why** an event was flagged,
instead of returning an opaque black-box score.

Deliberately built on **rules + statistical anomaly scoring, not deep
learning**, so every decision is explainable and auditable — this matters
more than marginal accuracy gains in a banking/regulatory context.

## Current progress (early build)

- [x] Repo structure + FastAPI backend skeleton
- [x] Core scoring engine (`app/engine/scoring.py`) with 4 of 5 signals wired
- [x] `/api/score-event` endpoint working end-to-end
- [x] Basic tests passing (`pytest`)
- [x] Synthetic data generator stub (normal vs. attack sequences)
- [ ] Time-since-last-activity signal (in progress)
- [ ] Full synthetic dataset generator at scale
- [ ] React analyst dashboard
- [ ] Threshold tuning against generated dataset
- [ ] Demo video

This is an idea + early-implementation stage submission — see `docs/` for
the Round 1 pitch deck content.

## Project structure

```
swapshield/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entrypoint
│   │   ├── routes/events.py     # API routes
│   │   ├── engine/scoring.py    # Rules + anomaly scoring engine (core logic)
│   │   ├── models/schemas.py    # Pydantic request/response schemas
│   │   └── data/generator.py    # Synthetic dataset generator
│   ├── tests/test_scoring.py
│   └── requirements.txt
├── frontend/                    # React dashboard (not yet started)
└── docs/                        # Deck content, notes, references
```

## Running it locally

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/docs` for interactive API docs, or POST
to `/api/score-event` with a JSON event body, e.g.:

```json
{
  "user_id": "demo_user",
  "event_type": "transaction",
  "device_id": "device_unknown_999",
  "latitude": 25.0,
  "longitude": 90.0,
  "sim_change_flag": true,
  "sim_change_minutes_ago": 10,
  "transaction_amount": 50000
}
```

Run tests:

```bash
cd backend
pytest
```

## Tech stack

- Backend: Python, FastAPI
- Frontend (planned): React.js, Tailwind CSS
- Scoring: rule-based + statistical anomaly detection (no ML training required)

## Team

Ashritha Dulam — solo submission
