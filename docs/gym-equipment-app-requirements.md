# Workout Tracker + Community Gym Equipment Map — Requirements

**Status:** Draft v0.1
**Owner:** Gabe
**Date:** 2026-11-04

---

## 1. Problem Statement

Gyms rarely publish a specific equipment inventory. Users can't plan a workout for an unfamiliar gym (travel, new membership, day pass) without visiting first, and existing workout trackers don't know what equipment a given gym has. The two problems share one data source: every logged set is an implicit observation that *this machine exists at this gym*.

## 2. Vision

A workout-tracking app where logging a workout at a gym passively builds a crowd-sourced, per-location equipment inventory that the whole community can browse.

**Two sides of the same data:**

| User benefit (private) | Community benefit (public) |
|---|---|
| Track sets, reps, weight, progress over time | See exactly what equipment a gym has before visiting |
| Plan workouts against equipment known to exist at "my gym" | Equipment freshness, condition, and crowding signals |
| Auto-substitute exercises when traveling | Compare gyms by equipment before joining |

## 3. Goals & Non-Goals

### Goals
- Make logging a workout fast enough that it beats pen-and-paper or Notes.
- Every logged exercise tagged to a gym contributes to that gym's equipment inventory with zero extra effort.
- Any user can look up a gym and see a confidence-weighted equipment list.
- Workout templates adapt to the equipment available at the selected gym.

### Non-Goals (v1)
- Social feed, followers, likes, or leaderboards.
- Coaching, AI-generated programming, or form analysis.
- Class schedules, membership pricing, or booking.
- Wearable / HR integration.
- Gym-operator dashboards (potential v2 revenue line).

## 4. Target Users

1. **The planner** — follows a program, needs to know if a gym has the racks/machines the program calls for.
2. **The traveler** — hotel gym, day pass, new city; wants to walk in with a workout already adjusted to what's there.
3. **The shopper** — choosing between gyms, wants an equipment comparison instead of marketing photos.
4. **The contributor** — regular at one gym, willing to log and flag what's there (and what's broken).

## 5. Core Concepts / Data Model

| Entity | Key fields | Notes |
|---|---|---|
| **Gym** | id, name, chain (nullable), address, lat/lng, hours (optional) | Seeded from Google Places / OSM; user-creatable with dedup |
| **Equipment type** | id, canonical name, category (free weight, machine, cable, cardio, rack/platform, specialty bar, other), aliases, brand variants | Curated master list; users can propose additions |
| **Gym equipment record** | gym_id, equipment_type_id, quantity (optional), condition, confidence score, first_seen, last_seen, source (logged / explicit / photo) | Derived + explicit; this is the community layer |
| **Exercise** | id, name, muscle groups, required equipment type(s), alternatives | Links workouts to equipment |
| **Workout** | id, user_id, gym_id, started_at, ended_at, notes | |
| **Set** | workout_id, exercise_id, weight, reps, RPE (optional), order | |
| **Template** | user_id, name, ordered exercises with target sets/reps | |
| **Report** | gym_id, equipment_type_id, user_id, type (present / missing / broken / fixed), photo (optional), timestamp | Explicit community input |

## 6. Functional Requirements

### 6.1 Workout Tracking (user side)
- **FR-1** Start a workout, select a gym (default: last used; nearby via location).
- **FR-2** Add exercises via search; log weight/reps per set; rest timer.
- **FR-3** Save and reuse templates; start a workout from a template.
- **FR-4** History view: per-exercise progression (max weight, volume, est. 1RM), per-workout log.
- **FR-5** Offline logging with sync on reconnect (gyms have bad signal).
- **FR-6** Export personal data (CSV).

### 6.2 Equipment Inventory (community side)
- **FR-7** Logging an exercise at a gym automatically upserts a *gym equipment record* for that exercise's required equipment (source = logged).
- **FR-8** Users can explicitly add / confirm / flag equipment at a gym (source = explicit), optionally with a photo.
- **FR-9** Users can report equipment as **broken** or **removed**; a configurable number of independent reports or days of no activity decays the confidence score.
- **FR-10** Gym page shows equipment grouped by category, with confidence (e.g., "Confirmed by 14 users, last seen 2 days ago") and condition flags.
- **FR-11** Equipment search: "gyms near me with a belt squat / reverse hyper / Smith machine."
- **FR-12** Gym comparison: side-by-side equipment lists for 2–3 gyms.

### 6.3 Equipment-Aware Planning
- **FR-13** When starting a template at a gym, flag exercises whose required equipment is not confirmed there and suggest alternatives (from the exercise alternatives map).
- **FR-14** Traveler mode: given a destination gym, show a "what you can and can't do here" diff against the user's active program.

### 6.4 Data Quality & Trust
- **FR-15** Confidence score = f(number of distinct contributors, recency, source type). Logged sets weight lower than explicit confirmations; photos weight highest.
- **FR-16** Rate-limit and dedupe contributions per user per gym per equipment type.
- **FR-17** Gym dedup on create (name + proximity fuzzy match) with a merge path for admins.
- **FR-18** Flag/report abuse; soft-delete with audit trail.

## 7. Non-Functional Requirements

- **NFR-1 Speed:** logging a set must take ≤ 2 taps from the workout screen.
- **NFR-2 Offline-first:** full logging works offline; inventory browsing cached for recently viewed gyms.
- **NFR-3 Privacy:** workout data private by default; only the *equipment observation* (gym, equipment type, timestamp) is shared — never weights, reps, or user identity on the public gym page.
- **NFR-4 Platforms:** iOS first, Android second; web for gym pages (SEO value — "does [gym] have a squat rack" is a real search query).
- **NFR-5 Scale target (v1):** 10k MAU, 5k gyms, 500k observations/month.

## 8. Cold-Start Strategy

The community layer is useless at zero data. Mitigations:
1. Seed gyms from Places/OSM; seed *chain-level* equipment baselines (e.g., Planet Fitness standard floor) marked as "unverified."
2. Make solo workout tracking good enough to use with no community data at all.
3. In-app prompt after a workout: "Confirm 3 pieces of equipment at [gym]?" — one-tap bulk confirm.
4. Launch city-by-city; Chicago first.

## 9. Monetization (later)

- Free: tracking + browsing.
- Pro: equipment-aware planning, traveler mode, advanced progression analytics.
- B2B (v2): verified gym profiles / operator-maintained inventory, listing promotion.

## 10. Success Metrics

| Metric | Target (6 months post-launch) |
|---|---|
| Weekly active loggers | 2,000 |
| Gyms with ≥ 10 confirmed equipment types | 500 |
| % workouts that contribute ≥ 1 new or re-confirmed observation | > 60% |
| Equipment page views from web search | 20k / month |
| D30 retention (loggers) | > 25% |

## 11. Open Questions

- Granularity: track *brand/model* (Hammer Strength ISO-Lateral Row) or just *type* (plate-loaded row)? Leaning type with optional brand tag.
- Quantity: do we track "3 squat racks" or just presence? Presence in v1; count as optional field.
- How to handle 24-hour access / multi-floor / annex gyms as one vs. many locations?
- Should hotel gyms be first-class (high traveler value, low contributor density)?
- Legal: any issue with users photographing inside private gyms? Likely terms-of-use disclaimer + photo optional.

## 12. MVP Scope (v1)

**In:** FR-1 to FR-5, FR-7, FR-8, FR-10, FR-11, FR-13, FR-15, FR-16, NFR-1 to NFR-3, iOS only, Chicago seed.
**Out:** FR-6, FR-9 decay logic (manual flag only), FR-12, FR-14, FR-17 admin merge, Android, web, monetization.
