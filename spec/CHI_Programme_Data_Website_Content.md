# Programme Data — Website Content & Build Notes

**For chidigitalexperience.org — CHI 2027 Programme Innovation**
Draft v0.1. Part A is publishable page copy. Part B is instructions for the site build.

---

# PART A — Page copy

> Publish at `chidigitalexperience.org/data`. Link from the main call to action and from the site navigation. Intended audience is everyone from a first-time hobbyist to a senior engineer, so it opens plainly and gets more technical as it goes.

---

## Programme Data

Everything you need to build against the CHI programme is a single JSON file. No API key, no sign-up, no approval step. You can start right now.

```
https://chidigitalexperience.org/data/chi2027/latest.json
```

That file contains the complete conference programme — every session, contribution, author, track, and room — and it updates as the programme changes, including during the conference itself.

### Available now

| Feed | What it is |
|---|---|
| `/data/chi2026/latest.json` | The full CHI 2026 programme. Real data, frozen. Best starting point. |
| `/data/chi2025/latest.json` | The full CHI 2025 programme. Real data, frozen. |
| `/data/sandbox/latest.json` | A synthetic programme at CHI 2027 scale. Deliberately awkward — see *Test against the sandbox*. |

### Available from April 2027

| Feed | What it is |
|---|---|
| `/data/chi2027/latest.json` | The real CHI 2027 programme, updating through to the end of the conference. |

The 2027 feed is published to everyone at the same URL, with no credentials. Teams whose apps are accepted will get it as part of the integration and testing window, but there is nothing to apply for and nothing to wait on — the structure is identical to the feeds above, so anything you build against CHI 2026 will work against CHI 2027 unchanged.

---

### Checking for updates

**Read this bit even if you skip the rest.** It is the one thing that is easy to get wrong, and getting it wrong means your app shows attendees a room that changed twenty minutes ago.

Each feed publishes a tiny `version.json` alongside the programme:

```json
{
  "edition": "chi2027",
  "revision": 17,
  "generated_at": "2027-05-12T09:14:22-04:00",
  "latest_url": "https://chidigitalexperience.org/data/chi2027/latest.json",
  "revision_url": "https://chidigitalexperience.org/data/chi2027/revisions/017.json"
}
```

Poll `version.json` with a unique query string, compare the revision to what you already hold, and only fetch the programme when it has moved:

```js
const BASE = 'https://chidigitalexperience.org/data/chi2027';

async function fetchProgrammeIfChanged(knownRevision) {
  // The ?t= makes every request a distinct URL, so no cache can answer it.
  const res = await fetch(`${BASE}/version.json?t=${Date.now()}`, {
    cache: 'no-store'
  });
  const { revision, revision_url } = await res.json();

  if (revision === knownRevision) return null;      // nothing new

  const programme = await fetch(revision_url).then(r => r.json());
  return { revision, programme };
}
```

Poll once a minute during the conference and you will never be more than a minute behind.

**Why the `?t=`.** Our hosting applies ten minutes of browser caching to every file and we cannot change that. A unique URL each time steps around it. The revision files it points you to never change once published, so you can cache those as long as you like — forever, ideally.

**About `latest.json`.** It always holds the current programme, and it is perfectly good for exploring the data, for scripts, and for apps that load once at startup. But because of that same ten-minute caching, **`latest.json` can be up to ten minutes out of date in a browser.** If your app needs to reflect live changes during the conference, use the pattern above instead. If it doesn't, `latest.json` is simpler and entirely fine.

---

### What's in the file

```json
{
  "edition": "chi2027",
  "revision": 17,
  "generated_at": "2027-05-12T09:14:22-04:00",
  "schema_version": "1.0",
  "conference": { "name": "ACM CHI 2027", "starts_on": "2027-05-10", … },
  "notices":       [ … ],
  "tracks":        [ … ],
  "venues":        [ … ],
  "sessions":      [ … ],
  "contributions": [ … ],
  "people":        [ … ]
}
```

| Collection | Contents |
|---|---|
| `sessions` | Title, type, start and end times, room, chairs, and the contributions within. |
| `contributions` | Individual papers and talks: title, abstract, authors, DOI, ACM DL link, keywords. |
| `people` | Authors and presenters — name, affiliation, and what they're involved in. |
| `venues` | Rooms and buildings, with floor, capacity, coordinates, and accessibility notes. |
| `tracks` | The programme's thematic and format groupings. |
| `notices` | Timestamped announcements, conference-wide or attached to a session. This is how you'll hear about a room flooding. |

A full JSON Schema is published at `/data/schema/v1.json` so you can generate types and validate locally.

**Four things worth knowing about the shape of the data:**

- **IDs are stable and never reused.** A session's ID is the same in the historical file, in the live feed, and after it gets moved. Use them as your keys with confidence.
- **Nothing is ever deleted.** A cancelled session stays in the file with `status: "cancelled"`. A moved session stays with `status: "relocated"` and a `status_note`. If you delete records that vanish from the feed, you'll be deleting nothing — but if you assume records never change, you'll show stale rooms.
- **Every record carries `last_modified`.** This is how you work out what to highlight to a returning user without diffing the whole file yourself.
- **Times carry an explicit offset** and the conference timezone is `America/New_York`. Please don't assume UTC.

---

### Test against the sandbox

`/data/sandbox/latest.json` is synthetic, sized like a real CHI, and seeded on purpose with everything that breaks conference apps:

- A paper with more than forty authors
- Emoji, Chinese, Japanese, Arabic and Hebrew text in titles and names
- A four-thousand-character abstract, and a six-word one
- LaTeX fragments and HTML entities in titles
- A session with no room assigned yet
- Two sessions overlapping in the same room; a 7am session; one crossing midnight
- Nulls in every optional field
- A cancelled session, a relocated one, and one rescheduled twice

All of this exists in real conference programmes. If your app survives the sandbox, it will survive May.

The accepted submission asks you to describe how your app handles updates. You won't have a live-changing feed to rehearse against before the conference — write your update logic against the pattern in *Checking for updates* and test it by hand: fetch `sandbox`, note the revision, wait, fetch again, and confirm your app picks up a change when one is published.

---

### What we don't provide

**We provide programme data, and nothing about the person using your app.** There is no login endpoint, no attendee directory, no way to ask us who someone is or whether they're registered. We don't offer it and we won't.

Personalisation is yours to build. Keep it in memory for the session, or in `localStorage` on the attendee's own device.

We think this is the better arrangement, and not only because it means there's nothing to wait for. An app that keeps preferences on the device and never transmits them is collecting no personal data at all — which makes the data protection requirements almost trivial to satisfy, and makes it much easier for attendees to trust what you've built. **The simplest way to pass our data protection hurdle is to not collect anything.** If your idea genuinely needs to know things about people, that's allowed, but you'll be asked to account for it.

Also not provided: full text or PDFs of papers. Every contribution carries its DOI and ACM Digital Library link, so link out instead.

---

### Fair use

There are no rate limits, because there's nothing to limit — these are static files behind a CDN, and you cannot realistically overload them. Two requests:

- Poll `version.json` no more than once every 30 seconds. Once a minute is plenty.
- Fetch the revision files rather than re-downloading `latest.json` in a loop. It's the same data and far kinder to everyone's bandwidth, including your users' mobile allowance.

### Licence

The programme data is published under **[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/)**.

In practice, for a competition entry:

- **Attribution.** Credit the source somewhere visible — an "about" screen or footer is fine. Suggested wording: *Programme data © ACM CHI 2027, licensed under CC BY-NC-SA 4.0.*
- **NonCommercial.** Entries must not be commercial. Distributing your app free of charge is fine. Selling it, putting it behind a paywall, or running advertising against it is not.
- **ShareAlike.** If you publish a modified or derived version of the data itself — a cleaned-up copy, a reshaped dataset, a set of embeddings you release — that derived data must carry the same licence. This applies to the *data*, not to your source code: simply reading and displaying the feed in your app does not make your app a derivative work.

You are welcome to commit copies of the data to your public repository. If you do, include a `LICENCE` or `DATA-LICENCE` file noting that the contents of that directory are CC BY-NC-SA 4.0, separately from whatever licence covers your code.

Unsure whether something you have in mind is permitted? Ask us — **app@chi2027.acm.org** — rather than guessing.

### Questions

Anything unclear, anything that looks wrong in the data, anything missing: **app@chi2027.acm.org**. If you find a bug in the feed, please tell us — you'll be doing every other entrant a favour.

---
---

# PART B — Build notes for the site

> To be folded into the website build specification given to Claude Code.

## B1. New page

Add a **Programme Data** page at `/data` (or `/data/` with the feed files beneath it — see B2 for the path collision note), containing Part A above.

- Link it prominently from the main call to action — the "what we'll provide" section should point here.
- Include it in the primary site navigation. It is one of the two pages entrants will actually read, alongside the submission requirements.
- Code blocks need syntax highlighting and a copy button. The JavaScript snippet in *Checking for updates* is the single most important thing on the site; assume people will copy it without reading around it, and make that easy.
- The *Checking for updates* section should be linkable directly (`/data#updates`) so we can point people at it in email.

## B2. Static data directory

The feed files live in the same repository and deploy as the site, under `/data/`.

**This must be passed through the site build completely untouched.** Static site generators routinely fingerprint, minify, rewrite, or relocate files they find in the source tree. These files have to arrive at exactly the documented paths, byte for byte, with exactly the documented names. Configure the generator's passthrough or `public/` equivalent accordingly, and add a build check that asserts the expected paths exist in the output.

Directory layout to create:

```
/data/
├── schema/v1.json
├── chi2025/latest.json
├── chi2026/latest.json
├── sandbox/{version.json, latest.json, revisions/}
└── chi2027/{version.json, latest.json, revisions/}
```

**Path collision:** if the documentation page is served at `/data`, make sure it does not shadow or get shadowed by the directory index. Either serve the page at `/data/` and the feeds beneath it, or put the page at `/programme-data` and keep `/data/` purely for files. The second is less elegant but less likely to break; the build spec should pick one and be explicit.

## B3. Hosting constraints to design around

Hosting is GitHub Pages.

- **No custom headers are possible.** GitHub Pages sets `Cache-Control: max-age=600` on everything and offers no configuration. This is why the documented consumption pattern uses a cache-busting query string; there is nothing the site build can do about it, and nothing it needs to do.
- **Verify CORS in the first deploy.** GitHub Pages sends `Access-Control-Allow-Origin: *`, which every browser-based entry depends on. Confirm it with an actual cross-origin fetch as part of the launch checklist — it is the one failure that would break every submission simultaneously.
- Serve everything over HTTPS on the custom domain, with HSTS enabled in the Pages settings.

## B4. Launch checklist for the data page

Before the call goes live on 11 September 2026:

- [ ] `chi2025`, `chi2026` and `sandbox` feeds published and reachable
- [ ] `schema/v1.json` published and validating against all three
- [ ] Cross-origin fetch confirmed from a third-party domain
- [ ] The code snippet in *Checking for updates* copied from the live page and run unmodified against `sandbox`, confirming it detects a manually-published revision change
- [ ] Verified from a cold browser on a mobile network, not just a desktop with devtools open
- [ ] `LICENCE` file present in `/data/`, and the licence stated in every feed's top-level metadata
- [ ] Licence questions in B6 resolved, or a licence FAQ line added to the page
- [ ] `app@chi2027.acm.org` receiving mail

## B6. Licence implementation

The data is licensed **CC BY-NC-SA 4.0**. Three things for the build:

- Add a `LICENCE` file at `/data/LICENCE` containing the full licence text and the attribution line.
- Add `"licence": "CC-BY-NC-SA-4.0"` and `"licence_url"` to the top-level metadata of every feed file, so the licence travels with the data rather than living only on a web page someone may never read.
- Link the licence from the data page and from the footer.

**Two open points that need resolving before launch** — see the discussion note accompanying this document:

1. Whether *NonCommercial* is intended to exclude industry entrants, and how it interacts with a free app that has any commercial dimension. A short FAQ line resolves most of this.
2. Whether we hold the rights to apply this licence to paper abstracts, as distinct from schedule facts. Worth a check with ACM/SIGCHI.

## B5. Copy change needed elsewhere

The main call to action currently describes a *"live JSON update API"*. That's now inaccurate, and the accurate version is a better pitch. Suggested replacement for that bullet:

> **A live-updating programme feed** — one URL, no API key, no sign-up. Historical CHI programme data is available from today, and the live CHI 2027 feed publishes in April.

Two further edits follow from dropping the keyed API:

- The April 2027 timeline row referring to *"release live programme JSON API credentials to accepted teams"* should become *"live programme feed published; integration and testing window opens"*.
- The accepted submission field on handling programme updates needs no change.

---
---

# PART C — Actual schema reference (source: `CHI_2026_program.json`)

> Part A describes the feed shape we intend to *publish* (`edition`, `revision`, `sessions`/`contributions`/`people`/…). The file the conference system actually exports today — `schemeVersion: 7` — has a different, more detailed shape. This section documents that real export as-is, so it can be used as the source of truth when building the transform into the public feed format, or handed to entrants directly if we decide to publish it unmodified. Field names below are exactly as they appear in the file (camelCase, unlike Part A's snake_case).

## C1. Top-level structure

```json
{
  "schemeVersion": 7,
  "cc_licence": "…",
  "conference": { … },
  "publicationInfo": { … },
  "sponsors": [ … ],
  "sponsorLevels": [ … ],
  "floors": [ … ],
  "rooms": [ … ],
  "tracks": [ … ],
  "contentTypes": [ … ],
  "timeSlots": [ … ],
  "sessions": [ … ],
  "events": [ … ],
  "contents": [ … ],
  "people": [ … ],
  "recognitions": [ … ]
}
```

| Collection | Contents |
|---|---|
| `conference` | Single object. Conference identity, dates, location, timezone, branding. |
| `publicationInfo` | Single object. Publish/draft flags and a monotonic `version` counter — the closest thing this export has to Part A's `revision`. |
| `sponsors` | Sponsor entries with logo, URL, HTML description, and a `levelId` into `sponsorLevels`. |
| `sponsorLevels` | Named sponsor tiers (Champion, Hero, Contributing, …) with a `rank` for ordering. |
| `floors` | Building floors, each with a map image and the `roomIds` located on it. |
| `rooms` | Physical rooms: capacity, seating setup, and a `typeId` restricting what content types may be scheduled there. |
| `tracks` | Thematic/organisational grouping applied to `contents` via `trackId`. Sparse — mostly a single `"Default"` track. |
| `contentTypes` | The fixed vocabulary of session/content kinds (Paper, Workshop, Panel, …), each with a display colour and a default duration in minutes. |
| `timeSlots` | Reusable `(startDate, endDate)` pairs that `sessions` point into. |
| `sessions` | Scheduled programme blocks: a room, a time slot, chairs, and the `contents` presented inside. |
| `events` | Standalone scheduled items (so far only type `Event`) that carry their own start/end times directly rather than via a `timeSlotId`. |
| `contents` | The actual papers/talks/submissions: title, abstract, authors, keywords, DOI/video links, awards. |
| `people` | Every author, chair, and presenter: name and affiliations. |
| `recognitions` | Award/recognition records referenced by `contents[].recognitionIds`. Empty in this export. |

**How the graph connects:** `sessions[].timeSlotId` → `timeSlots[].id`; `sessions[].roomId` → `rooms[].id`; `sessions[].contentIds` and `contents[].sessionIds` are the (redundant, both-directions) link between a session and what's presented in it; `contents[].eventIds` links a content item to an `events[].id` the same way; `sessions[].chairIds`, `events[].chairIds`/`presenterIds`, and `contents[].authors[].personId` all point into `people[].id`; `contents[].trackId` → `tracks[].id`; `contents[].typeId` / `sessions[].typeId` / `events[].typeId` / `rooms[].typeId` → `contentTypes[].id`.

All numeric IDs (`id` fields) are integers, stable within an export, and namespaced per collection (a `roomId` and a `personId` can share the same number).

---

## C2. `conference`

```json
{
  "id": 10142,
  "shortName": "CHI",
  "displayShortName": "",
  "year": 2026,
  "startDate": 1776038400000,
  "endDate": 1776384000000,
  "fullName": "ACM CHI Conference on Human Factors in Computing Systems",
  "url": "https://chi2026.acm.org",
  "location": "Barcelona International Convention Centre, Barcelona",
  "timeZoneOffset": 120,
  "timeZoneName": "Europe/Brussels",
  "logoUrl": "https://…",
  "accessibilityFaqUrl": "https://…",
  "addons": {},
  "name": "CHI 2026"
}
```

| Field | Type | Notes |
|---|---|---|
| `startDate`, `endDate` | integer | **Milliseconds since Unix epoch, UTC** — not ISO strings, unlike Part A. |
| `timeZoneOffset` | integer | Minutes east of UTC (e.g. `120` = UTC+2). |
| `timeZoneName` | string | IANA zone name. |
| `addons` | object | Free-form extension slots; empty in every example seen. |

## C3. `publicationInfo`

Draft/publish flags plus a `version` integer that increments on every re-export (`86` in this snapshot) — use it the way Part A uses `revision`. `publicationDate` is a `"YYYY-MM-DD HH:MM:SS+00"` string, not epoch millis or ISO-8601 `T`-separated.

## C4. `sponsors` / `sponsorLevels`

Each sponsor has a `levelId` into `sponsorLevels`; `sponsorLevels[].rank` gives display order (lower = more prominent). `sponsors[].description` is a raw HTML string (sanitise before rendering). `extraPadding` and `order` are presentation hints for the logo wall, in pixels and list order respectively.

## C5. `floors` / `rooms`

```json
// floors[]
{ "id": 10473, "name": "2. Convention Centre - P0", "mapImageUrl": "https://…", "roomIds": [12351, …] }

// rooms[]
{ "id": 12303, "name": "P1 - Room 111", "setup": "CLASSROOM", "typeId": 14694, "capacity": 236, "note": "Half theatre" }
```

- `rooms[].setup` is an enum: `THEATRE`, `CLASSROOM`, `ROUNDS`, `SPECIAL`, `NO_ROOM` (the last used for sessions with no physical room, e.g. livestream-only).
- `rooms[].typeId` → `contentTypes[].id`; it constrains/labels which kind of content the room is set up for, not a hard restriction.
- `note` is optional free text (e.g. `"Half theatre"`); no room capacity or GPS coordinates beyond the single integer `capacity`.
- There is no floor coordinate or accessibility field per room in this export, unlike the `venues` collection sketched in Part A.

## C6. `tracks`

```json
{ "id": 13827, "name": "Default" }
```

Minimal — just `id` and `name`. In this export almost every content item shares a single `"Default"` track; don't assume tracks carry colour/description metadata.

## C7. `contentTypes`

```json
{ "id": 14694, "name": "Paper", "displayName": "Papers", "color": "#0d42cc", "duration": 12 }
```

The fixed vocabulary referenced by `sessions[].typeId`, `contents[].typeId`, `events[].typeId`, and `rooms[].typeId`. `displayName` is optional (absent on a few types, e.g. `"Break"`). `duration` is the *default* length in minutes for one item of that type — a session or content item can override it (`sessions` via its time slot, `contents` via `durationOverride`).

Observed types: Course, Event, Paper, Workshop, Break, Journals, Interactive Demos, Plenary and Keynote, Meet-Ups, Posters, Panels, Student Research Competition, SIGCHI Awards, Student Mentoring Program, Global Plaza, Global Science Program.

## C8. `timeSlots`

```json
{ "id": 15387, "type": "SESSION", "startDate": 1776157200000, "endDate": 1776162600000 }
```

`startDate`/`endDate` are epoch milliseconds, UTC (add `conference.timeZoneOffset` minutes to get local time). `type` observed value: `"SESSION"`.

## C9. `sessions`

```json
{
  "id": 252065,
  "name": "Global Plaza fireside chat: Belonging at CHI…",
  "description": "…",
  "addons": {
    "Join Zoom Meeting": {
      "name": "Join Zoom Meeting",
      "title": "Meeting ID: 694 9509 5128 Passcode: 749990",
      "type": "custom",
      "url": "https://…"
    }
  },
  "isParallelPresentation": false,
  "importedId": "20756",
  "typeId": 14889,
  "roomId": 12403,
  "chairIds": [214298, 227959],
  "contentIds": [],
  "source": "SYS",
  "timeSlotId": 15391
}
```

| Field | Type | Notes |
|---|---|---|
| `roomId` | integer \| absent | May be missing for sessions with no assigned room. |
| `timeSlotId` | integer | → `timeSlots[].id`, gives the actual start/end. |
| `chairIds` | integer[] | → `people[].id`. Session chairs, not authors. |
| `contentIds` | integer[] | → `contents[].id`. Can be empty (e.g. non-paper sessions like the fireside chat above). |
| `addons` | object, keyed by label | Each value has its own `type`; observed session addon type: `custom` (used for join-links like Zoom). |
| `source` | string enum | `"SYS"` (added directly in the system) or `"PCS"` (imported from the submissions/review system). |
| `importedId` | string | Original ID in the source system; opaque, for traceability only. |
| `isParallelPresentation` | boolean | Marks sessions running concurrently with parallel tracks. |
| `description` | string \| absent | Plain/HTML text; often absent for straightforward paper sessions. |

Note there is no `status` (cancelled/relocated) or `last_modified` field on sessions in this export — the "nothing is ever deleted, everything has last_modified" guarantee described in Part A is a design goal for the *published* feed, not a property of this raw export. Any transform that builds the public feed needs to synthesize those fields (e.g. by diffing successive exports) rather than pass them through.

## C10. `events`

Structurally identical to `sessions` but self-contained: it carries `startDate`/`endDate` directly (epoch ms) instead of a `timeSlotId`, and `presenterIds` in addition to `chairIds`.

```json
{
  "id": …, "name": "…", "description": "…",
  "startDate": …, "endDate": …,
  "roomId": …, "chairIds": [ … ], "presenterIds": [ … ],
  "contentIds": [ … ], "typeId": 14692,
  "importedId": "…", "source": "SYS", "isParallelPresentation": false
}
```

Every `events[].typeId` observed in this export is `14692` (`"Event"`).

## C11. `contents`

The papers/talks/submissions themselves — by far the largest and richest collection (2,782 entries).

```json
{
  "id": 222414,
  "typeId": 14694,
  "title": "Challenges in Synchronous & Remote Collaboration Around Visualization",
  "addons": {
    "doi": { "name": "doi", "title": "Open in ACM DL", "type": "doiLink", "url": "https://doi.org/10.1145/…" },
    "Presentation Video": { "title": "Presentation Video", "type": "video", "url": "https://www.youtube.com/watch?v=…" }
  },
  "recognitionIds": [],
  "isBreak": false,
  "importedId": "chi26c-9318",
  "source": "PCS",
  "trackId": 13833,
  "tags": [],
  "keywords": [],
  "sessionIds": [225146],
  "eventIds": [],
  "abstract": "…",
  "authors": [
    {
      "personId": 220692,
      "affiliations": [
        { "country": "Canada", "state": "Ontario", "city": "Waterloo", "institution": "University of Waterloo", "dsl": "School of Computer Science" }
      ]
    }
  ],
  "award": "BEST_PAPER",
  "durationOverride": 20
}
```

| Field | Type | Notes |
|---|---|---|
| `typeId` | integer | → `contentTypes[].id`. |
| `trackId` | integer | → `tracks[].id`. |
| `sessionIds` / `eventIds` | integer[] | Where this content is presented; both are usually singleton arrays but modelled as arrays (a content item could in principle appear in more than one). |
| `authors` | object[] | Each entry has `personId` (→ `people[].id`) **and its own `affiliations` array** — affiliation is captured per-paper, not just on the person record, since the same author's affiliation can change between papers/years. |
| `authors[].affiliations[]` | object | `country`, `state`, `city`, `institution`, and optionally `dsl` (department/school/lab) — all strings, any of which may be `""`. |
| `award` | string enum \| absent | Observed values: `"BEST_PAPER"`, `"HONORABLE_MENTION"`. Absent (not null) when the content has no award. |
| `recognitionIds` | integer[] | → `recognitions[].id`. Always empty in this export (the `recognitions` collection itself is empty). |
| `durationOverride` | integer \| absent | Minutes. Overrides the `contentTypes[].duration` default for this specific item (e.g. a 20-minute keynote where the type default is 70). |
| `isBreak` | boolean | Marks scheduling filler (coffee breaks etc.) rather than real content. |
| `tags`, `keywords` | string[] | Both present as separate arrays; empty in most sampled records. |
| `addons` | object, keyed by label | Observed `type` values: `doiLink` (ACM DL link), `video` (recording), `config` (presentation styling, e.g. `{"config": {"type": "config", "label": {"title": "Sustainable Practice", "color": "aquamarine"}}}` — a coloured badge shown on the item). |
| `abstract` | string | Plain text; may contain literal `\r\n` line breaks. |
| `source` / `importedId` | as in `sessions` | `importedId` for PCS-sourced content is the submission's PCS paper ID (e.g. `"chi26c-9318"`). |

## C12. `people`

```json
{
  "id": 230292,
  "firstName": "Max",
  "lastName": "Birk",
  "middleInitial": "",
  "importedId": "27",
  "source": "SYS",
  "affiliations": [
    { "country": "Netherlands", "state": "North Brabant", "city": "Eindhoven", "institution": "Eindhoven University of Technology" }
  ]
}
```

A person-level `affiliations` array exists alongside the per-authorship one on `contents[].authors[].affiliations` — treat the person-level one as "current/primary" and the authorship-level one as "as credited on that specific paper"; they can differ and either can be empty. There is no email, ORCID, photo, or bio field in this export — just name, affiliation, and identifiers.

## C13. `recognitions`

Empty (`[]`) in this export; presumably objects describing named awards (e.g. best-paper committee, honourable-mention criteria) that `contents[].recognitionIds` would reference when populated. Schema unknown until a populated example is available.

## C14. Cross-cutting conventions in this export

- **Dates** are epoch milliseconds (UTC) everywhere except `publicationInfo.publicationDate`, which is a space-separated `"YYYY-MM-DD HH:MM:SS+00"` string. Neither matches Part A's ISO-8601-with-offset convention — any transform into the public feed format needs to normalise this.
- **`source`** is a two-value enum (`SYS` / `PCS`) on `sessions`, `events`, `contents`, and `people`, marking whether the record was entered directly in the conference-management system or imported from the paper-submission system.
- **`importedId`** is always a string (even when it looks numeric) and is only meaningful within its own `source` system — don't treat it as a stable cross-export identifier the way `id` is.
- **`addons`** is a recurring extension pattern (on `conference`, `sessions`, `events`, `contents`) — an object keyed by a human label, each value carrying its own `type` and type-specific fields (`url`, `label`, etc.). Treat unknown `addons` types as safe to ignore/pass through rather than erroring.
- **Optional fields are typically omitted, not `null`.** Code reading this export should use "key present" checks (`'roomId' in session`) rather than null checks in most cases — confirmed for `roomId`, `award`, `durationOverride`, `description`, `note`.
- This export has **no explicit `status`, `last_modified`, or soft-delete markers** anywhere. If the public feed's change-tracking guarantees (§ "What's in the file" in Part A) are to hold, they must be computed by the export/transform pipeline by diffing this file against the previous export, not read directly off it.
