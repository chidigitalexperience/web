# CHI 2027 Programme Innovation — Programme Data Specification

**Draft v0.2 — for internal discussion**
Prepared for the Programme Innovation chairs, CHI 2027 (10–14 May 2027, Pittsburgh, PA)

> **Supersedes v0.1**, which specified a REST API with keyed access. That has been replaced by a single versioned JSON file served statically. See §7 for what changed and the knock-on edits needed in the competition materials.

---

## 1. What we provide

One JSON file per conference edition, containing the complete programme, served over HTTPS from a static host. It carries its own version number and is updated in place as the programme changes.

That's the whole thing. No API keys, no query parameters, no server-side logic, no rate limits worth mentioning.

**Explicitly not provided:**

- Any user identity, account, sign-in, or registration-validation endpoint
- Attendee lists, registration records, or any personal data about attendees
- Full text or PDFs of papers

Personalisation is the app's responsibility, held transiently or in client-side storage on the attendee's own device (see §6).

---

## 2. URLs

```
https://chidigitalexperience.org/data/
├── chi2027/
│   ├── version.json          ← tiny; poll this
│   ├── latest.json           ← the current programme
│   └── revisions/
│       ├── 001.json          ← immutable, permanent
│       ├── 002.json
│       └── …
├── chi2026/latest.json       ← historical, frozen
├── chi2025/latest.json       ← historical, frozen
└── sandbox/latest.json       ← synthetic, 2027-scale, frozen
```

Serving from a path on the main site rather than a subdomain means one repository, one deployment, and no extra DNS or certificate to arrange. It also puts the data immediately alongside the documentation page that describes it, which is where entrants will look first.

Two practical consequences to hand to whoever builds the site:

- **The `/data` directory must be passed through untouched by the site build.** Most static site generators will try to process or fingerprint files they find in the source tree; these files need to arrive at exactly the documented paths with exactly the expected names.
- **No cache configuration is possible on GitHub Pages** (§3), so the freshness of the data is handled entirely by how apps request it. Nothing for the site build to do here — but nothing it can do to help, either.

**`version.json`** is a few hundred bytes and exists purely so apps can check for updates cheaply:

```json
{
  "edition": "chi2027",
  "revision": 17,
  "generated_at": "2027-05-12T09:14:22-04:00",
  "latest_url": "https://chidigitalexperience.org/data/chi2027/latest.json",
  "revision_url": "https://chidigitalexperience.org/data/chi2027/revisions/017.json"
}
```

An app polls this, compares the revision against what it holds, and only refetches the full file when it has moved. This is the entire change-detection mechanism and it needs no server.

**`latest.json`** is the same content as the newest revision file. Two copies of the same bytes — deliberately, so that apps can either track the moving target or pin to something immutable.

**`revisions/NNN.json`** are never modified or deleted once published. They give us free rollback, and give teams a stable reference for debugging ("it worked on revision 14").

---

## 3. Caching on GitHub Pages

This is the one genuine constraint in the whole design, so it is worth being precise about.

**GitHub Pages sets `Cache-Control: public, max-age=600` on every file it serves, and provides no way to change it.** There are no custom headers, no `_headers` file, no configuration. Ten minutes of browser caching is imposed on us.

The good news is that GitHub purges its own CDN edge on every deploy, so the edge is fresh the moment we push. The ten minutes applies to browser caches and any intermediate proxy — which is still enough to have an attendee looking at a room that changed nine minutes ago.

We do not fix this with headers. We design so that it cannot matter.

### 3.1 The approach: only one file ever needs to be fresh

`revisions/NNN.json` never changes once published. Caching it for ten minutes, or ten years, is harmless and in fact desirable.

So the only file whose freshness matters is `version.json` — a few hundred bytes. And a browser cache keys on the **full URL including the query string**, so appending a unique value defeats it completely:

```
GET /data/chi2027/version.json?t=1778935200
```

Each poll is a distinct URL, so nothing can serve it from cache, and it costs a few hundred bytes. The app then fetches `revisions/NNN.json`, which is immutable and safe to cache indefinitely.

This sidesteps the ten-minute window entirely. It does not mitigate it or work around it — the stale copy is never consulted, because the app never asks for the same URL twice.

### 3.2 The documented pattern for entrants

This needs to be the *first* thing in the participant documentation, with working code, because the obvious naive approach — poll `latest.json` — is the one that inherits the ten-minute delay. Left to themselves, most teams will do exactly that.

```js
const BASE = 'https://chidigitalexperience.org/data/chi2027';

async function fetchProgrammeIfChanged(knownRevision) {
  // Unique URL every time: cannot be served from any cache.
  const res = await fetch(`${BASE}/version.json?t=${Date.now()}`, {
    cache: 'no-store'
  });
  const { revision, revision_url } = await res.json();

  if (revision === knownRevision) return null;   // nothing new

  // Immutable file — cache it forever, quite deliberately.
  const programme = await fetch(revision_url).then(r => r.json());
  return { revision, programme };
}
```

Poll every 60 seconds during the conference and the worst-case staleness is 60 seconds, not ten minutes. `{ cache: 'no-store' }` is belt and braces alongside the query string.

### 3.3 What `latest.json` is for

It remains, but as a convenience for casual and one-shot consumers: someone exploring the data, a script, a build-time fetch, an app that loads once and doesn't care about live updates.

Its documentation should state plainly: **`latest.json` may be up to ten minutes stale, by design. Apps that need live updates during the conference must use the `version.json` + revision pattern in §3.2.** Better to say so than to have a team discover it on the Tuesday.

### 3.4 If we later decide ten minutes is unacceptable even as a fallback

Two escape hatches, neither needed if §3.2 is followed:

- **Put Cloudflare's free tier in front of the custom domain.** GitHub Pages remains the origin; Cloudflare Cache Rules give full control over `Cache-Control` per path. Roughly an afternoon of work.
- **Deploy to Cloudflare Pages instead**, which supports a `_headers` file. Same Git-based workflow, same repository, same publishing script — only the deploy target changes.

Worth knowing these exist. Not worth doing pre-emptively.

### 3.5 Other headers

- **CORS:** GitHub Pages sends `Access-Control-Allow-Origin: *` on static assets already, which is what every browser-based entry needs. Verify it early anyway — it is the single failure that would break every submission at once.
- **ETag / Last-Modified:** sent automatically. Fine.
- **Compression:** gzip is applied automatically. A full CHI programme is a few MB raw and compresses well.

### 3.6 Test before September, not in May

Publish a change to the sandbox, then confirm from a cold browser on a mobile network that the `version.json` poll picks it up within a minute. Ten minutes of imposed caching is survivable; discovering during the conference that we misunderstood it is not.

---

## 4. File contents

A single document containing every collection, with version metadata at the top so the file is self-describing:

```json
{
  "edition": "chi2027",
  "revision": 17,
  "generated_at": "2027-05-12T09:14:22-04:00",
  "schema_version": "1.0",
  "conference": {
    "name": "ACM CHI 2027",
    "starts_on": "2027-05-10",
    "ends_on": "2027-05-14",
    "timezone": "America/New_York",
    "city": "Pittsburgh, PA"
  },
  "notices": [ … ],
  "tracks": [ … ],
  "venues": [ … ],
  "sessions": [ … ],
  "contributions": [ … ],
  "people": [ … ]
}
```

### Principles that still hold from v0.1

1. **One schema throughout.** Historical editions, sandbox, and the live 2027 file are structurally identical. A team building against CHI 2025 data in October must not have to re-engineer in April.
2. **Frozen at launch.** `schema_version` 1.0 is fixed when the CTA publishes on 11 September 2026. Additive changes only thereafter.
3. **Stable IDs, never reused.** If a session ID changes between the historical file and the live one, every app breaks silently.
4. **Nothing ever disappears.** Cancelled and moved sessions stay in the file with a changed `status`. Removing records leaves cached apps showing ghosts and diffing apps crashing.

### Session

```json
{
  "id": "s-2027-0388",
  "title": "Designing for Serendipity",
  "session_type": "paper_session",
  "track_ids": ["t-interaction"],
  "starts_at": "2027-05-12T11:00:00-04:00",
  "ends_at": "2027-05-12T12:20:00-04:00",
  "venue_id": "v-room-315",
  "chair_person_ids": ["p-01942"],
  "contribution_ids": ["c-2027-1187", "c-2027-1204"],
  "status": "relocated",
  "status_note": "Moved from Room 210 due to capacity.",
  "is_hybrid": true,
  "stream_url": null,
  "last_modified": "2027-05-12T08:51:03-04:00"
}
```

`status` ∈ `scheduled` | `rescheduled` | `relocated` | `cancelled` | `tba`.

Per-record `last_modified` matters more now than it did with a delta endpoint: it is how an app that holds an older copy works out what to highlight to the user, without us having to compute diffs.

### Contribution

`id`, `session_id`, `title`, `abstract`, `contribution_type`, `author_person_ids`, `doi`, `acm_dl_url`, `keywords`, `award`, `status`, `last_modified`.

Abstract inclusion depends on redistribution rights (§8). `doi` and `acm_dl_url` let apps link out in place of full text.

### Person

Presenters and authors only — people already public in the programme. `id`, `display_name`, `affiliation`, `orcid`, `contribution_ids`, `session_ids`. No email addresses, no photos, no attendee records.

### Venue

`id`, `name`, `building`, `floor`, `capacity`, `latitude`, `longitude`, `accessibility_notes`, `parent_venue_id`.

### Notice

Timestamped free-text announcements, conference-wide or scoped to a session. `id`, `severity`, `title`, `body`, `scope`, `entity_ids`, `published_at`, `expires_at`. Cheap to include, and the thing we'll be most grateful for when a room floods on the Wednesday.

---

## 5. Sandbox and test data

Worth more attention than it usually gets, because "your app must handle programme updates during the event" is untestable without it — and unassessable by the jury.

**`sandbox/latest.json`** — a synthetic programme at realistic 2027 scale, frozen, seeded with the things that break apps:

- A contribution with 40+ authors
- Emoji, CJK, RTL text and combining diacritics in titles and names
- A 4,000-character abstract and a 6-word one
- LaTeX fragments and HTML entities in titles
- A session with `venue_id: null` and `status: "tba"`
- Overlapping sessions in one room; a 07:00 session; a session crossing midnight
- Nulls in every optional field
- A cancelled session, a relocated one, and one rescheduled twice

Teams will meet all of this in the real data. Far cheaper for them to meet it in November.

There is no live-changing sandbox feed. A team verifies their update handling by re-fetching `sandbox/latest.json` and `version.json` by hand after we publish a deliberate change, rather than against something that mutates on its own on a schedule.

---

## 6. Personalisation is the app's responsibility

We provide no identity or user-information endpoint of any kind. Apps that personalise must do so themselves, transiently or in client-side storage on the attendee's own device.

This should be communicated to entrants as guidance rather than a bare limitation, because it does useful work for us:

- **It removes a barrier to entry.** No credentials to wait for, no OAuth integration. A team can build a fully personalised experience against the open historical file in September.
- **It keeps the privacy surface small.** An app holding preferences in `localStorage` that never transmits them collects no personal data at all — which is the shortest route through the data protection hurdle. Telling entrants this plainly nudges them toward the design we'd prefer anyway.
- **It avoids a single point of failure.** No shared auth service to fall over on the Tuesday.

Entrants should be told up front, since several of the ideas the call invites — community-finding, meet-ups, connecting first-timers — will otherwise be scoped on an assumption that we supply attendee identity.

---

## 7. Publishing and backup workflow

This is now the substance of the work. The delivery mechanism is trivial; the operational discipline around updating the file is what determines whether it works during the conference.

### 7.1 Repository as the system

Hold the data in a Git repository and publish the repository itself as the static site (GitHub Pages, Cloudflare Pages, Netlify — any of them). This gives us, for no additional effort:

- **Backups** — every revision is a commit, replicated wherever the repo is cloned
- **Provenance** — who published what, when, and why, in the commit log
- **Diffs** — a readable record of exactly what changed between revisions
- **Rollback** — revert and push
- **Publishing** — the deploy is the push

There is no database and no server to maintain, which matters a great deal for a system that has to be operable at 08:00 on a Tuesday by whoever is awake.

### 7.2 Publish sequence

```
1. Export from upstream (see §8, Q1)
2. Transform to the CHI 2027 schema
3. VALIDATE  ← gate; abort on failure
4. Increment revision; stamp generated_at
5. Write revisions/NNN.json
6. Copy to latest.json
7. Write version.json
8. Commit with a message naming what changed
9. Push → deploy
10. Verify from an external network
```

Steps 3 to 9 should be one script and one command. If publishing an update is fiddly, it won't happen promptly during the conference, and the whole value proposition of a live feed evaporates.

### 7.3 Validation gate

The realistic catastrophic failure is not the site going down — a CDN is more reliable than anything we'd build. It is **publishing a broken or empty file over a good one**. The validation step therefore matters more than everything else in this document:

- Validates against the published JSON Schema
- No duplicate, null, or missing IDs
- Every `venue_id`, `session_id`, `track_id`, `person_id` reference resolves
- Every timestamp parses and carries an offset
- Record counts within a sane band of the previous revision (abort if sessions drop by more than, say, 5% without an explicit override flag)
- File size within a sane band of the previous revision

Abort the publish on any failure. `latest.json` keeps pointing at the last good revision, which is exactly the behaviour we want.

### 7.4 Rollback

Copy the last known-good revision file over `latest.json`, bump `version.json`, commit, push. Under a minute, and it should be written down as a runbook rather than worked out under pressure. Published revision files are never modified or deleted — that's what makes rollback safe.

### 7.5 Operational commitments

| Commitment | Proposed |
|---|---|
| Update latency during the event | Changes visible to polling apps within 30 minutes of entry in the official system (publish time + ~1 min poll interval; see §3) |
| Historical data available | Live on the CTA launch date, 11 September 2026 |
| Support window | Named contact, 07:00–20:00 ET, 10–14 May 2027 |
| Uptime | Whatever the static host offers; realistically better than we could promise ourselves |

The latency figure is the one to be careful with. If the file is regenerated by a person running an export rather than automatically, "live" means "as often as someone does it" — and the published number should reflect that honestly rather than aspirationally.

---

## 8. Open questions

1. **Upstream source.** Is the file generated automatically from the official scheduling system (QOALA / programs.sigchi.org), or by hand? Determines whether §7.5's latency figure is credible, and how much of §7.2 is build versus transform.
2. **Abstract redistribution rights.** Can we serve abstracts in an openly accessible file? If not, apps lose most of their content-matching capability and we should say so early.
3. **Data licence — decided as CC BY-NC-SA 4.0, with two loose ends.** (a) Does *NonCommercial* exclude industry entrants, and does a free app with any commercial dimension fall foul of it? (b) Do we hold the rights to apply this licence to paper abstracts, as opposed to schedule facts? Both need a line of clarification rather than a change of licence.
4. **Venue and floorplan data.** Room names alone won't support wayfinding. Worth asking the local chairs now — venue data is usually trapped in a PDF and takes months to prise out.
5. **Who publishes.** Who runs the update during the conference, and who is their backup? Also who generates the historical files for September.
6. **Relationship to the official programme app.** Does it draw on the same source? If so, our file inherits its correctness requirements.

**Settled:** no user identity or attendee-information endpoint (§6). No API keys or per-team credentials (§9).

---

## 9. What changed from v0.1, and the knock-on edits

| v0.1 | v0.2 | Consequence |
|---|---|---|
| REST endpoints per collection | One file | Apps filter in memory. A few MB is trivial for this. |
| `/changes?since=` delta endpoint | Per-record `last_modified` | Apps diff client-side. They hold the whole file regardless. |
| API keys for accepted teams | None | See below — this affects the published timeline. |
| Query filters | None | Same as above; filtering client-side is fine at this scale. |
| Per-key usage analytics | CDN aggregate only | We lose per-team usage figures for the retrospective. Recoverable if teams self-report. |
| Rate limits | Not needed | A CDN absorbs anything the competition can generate. |

**Two edits needed in the existing competition materials:**

1. **The timeline row for April 2027** currently reads along the lines of *"release live programme JSON API credentials to accepted teams"*. There are no credentials. It should become something like *"live programme feed published; integration and testing window opens"*.
2. **The CTA's "What we'll provide" section** describes a *"live JSON update API"*. More accurate, and more appealing to the vibe-coding audience we're courting, would be a *"live-updating JSON feed — one URL, no API keys, no sign-up"*. The simplicity is a selling point rather than something to apologise for.

The accepted submission field asking how the app *"receives and reflects programme updates pushed during the event"* still works unchanged, and is testable against `sandbox` by manually publishing a change and confirming the app picks it up.
