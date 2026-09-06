# CHI 2027 Digital Experience Competition — Website Build Specification

*A spec for building the custom competition site. Intended to be handed to Claude Code.*

---

## 1. Overview

We are running a Digital Experience Competition for **ACM CHI 2027** (10–14 May 2027, Pittsburgh, PA). Developers, designers, and researchers are invited to build apps and tools that innovate the *attendee experience* of the conference — going beyond the official programme app, which already exists.

This spec is for the **custom competition website**, which will live at **chidigitalexperience.org**. Promotional material and the top-level call-to-action live separately on the main CHI WordPress site and link here. This site is the operational home of the competition: it hosts the detail, the data, the documentation, and the submission process.

**This site owns:**

- Full competition details, timeline, judging information
- Documentation of the data and API we provide
- The data downloads and API access
- FAQ / Q&A
- The submission forms (initial and accepted stages)

**This site does *not* own:**

- The promotional CTA (that lives on the main CHI site and links here)

---

## 2. Audience

1. **Applicants** — primarily developers, but ranging from students and hobbyists to professionals. Assume a technical audience for the data/API pages, but keep the overview and entry flow approachable to non-experts.
2. **Administrators (chairs)** — need to receive, view, and export submissions. A lightweight admin view is in scope (see §7).
3. **Judges** — will review submissions. Judge tooling can be minimal for v1 (exported data is acceptable); flag as a possible future enhancement.

---

## 3. Site map

| Page | Purpose |
|---|---|
| **Home / Overview** | What the competition is, the framing, the incentives, key dates, and a clear path to "Enter". Mirrors the CTA but is the fuller version. |
| **What We Provide** | Points to the **Programme Data** page for the full data/feed documentation, plus the compute/LLM credits offer. |
| **Programme Data** | Full documentation of the programme data feed — see §4a and [CHI_Programme_Data_Website_Content.md](CHI_Programme_Data_Website_Content.md), which is the source of truth for this page's content and build. |
| **Timeline** | Full timeline and key dates. |
| **Judging** | Acceptance hurdles (pass/fail) and scored criteria, jury composition, and category awards. |
| **Enter (Initial Submission)** | The initial submission form. See §5. |
| **Accepted Teams** | Information and the accepted-stage submission form. Gated or unpublished until the notification stage. See §6. |
| **FAQ** | Q&A. Should be easy for chairs to update without a developer (see §7). |
| **Contact** | How to reach the chairs — email app@chi2027.acm.org (also the address for judging enquiries and general queries). |

Navigation should make **Enter** prominent throughout.

---

## 4. Key content

The following content is finalised and should be used verbatim where practical. British English spelling throughout ("programme", "finalise", "licence").

### Key dates

| Milestone | Date |
|---|---|
| Submissions open | Friday 11 September 2026 |
| Prototype deadline | Friday 4 December 2026 |
| Notification | End of January 2027 |
| Live programme feed published; integration & testing window opens | April 2027 |
| ACM CHI 2027 | 10–14 May 2027, Pittsburgh, PA |

### What we provide

- **A live-updating programme feed** — one URL, no API key, no sign-up. Historical CHI programme data (CHI 2025, CHI 2026) is available from today, plus a synthetic sandbox feed at CHI 2027 scale for testing. The live CHI 2027 feed publishes at the same URL in April 2027; there is nothing to apply for. Full documentation lives on the **Programme Data** page — see §4a.
- **Compute / LLM API credits** — pending sponsorship; present as "watch this space".

> **Note — supersedes an earlier "live JSON update API with issued credentials" framing.** There is no keyed API and no credential-issuance step. See §4a and [CHI_Programme_Data_Website_Content.md](CHI_Programme_Data_Website_Content.md) for the current, correct model, and update the April 2027 timeline wording accordingly (§4).

---

## 4a. Programme Data page

The **Programme Data** page (`/data` or `/programme-data` — see path-collision note below) is one of the two pages entrants will actually read, alongside the submission requirements. Its full page copy and build notes are specified separately in **[CHI_Programme_Data_Website_Content.md](CHI_Programme_Data_Website_Content.md)**, Part A (page copy) and Part B (build instructions). Treat that document as authoritative for this page and fold its Part B notes into the build:

- **Single JSON feed, publicly reachable, no auth** — `https://chidigitalexperience.org/data/{edition}/latest.json`. Feeds available immediately: `chi2025`, `chi2026` (frozen, real data), and `sandbox` (synthetic, CHI-2027-scale, deliberately awkward edge cases). The real `chi2027` feed goes live at the same path in April 2027 — same schema, no separate credentialing step. There is no live-changing sandbox feed — entrants test update handling by manually re-fetching `sandbox` after a change is published, not against a feed that mutates on its own.
- **Update pattern via `version.json` + revision polling** — the page must present the cache-busting polling pattern (poll `version.json` with a unique query string, compare `revision`, fetch the immutable `revision_url` only when it has moved) as the primary, correctly-highlighted code sample. This exists because GitHub Pages hosting applies non-configurable 10-minute caching (see §10/hosting below); `latest.json` alone can be up to 10 minutes stale.
- **JSON Schema published** at `/data/schema/v1.json`.
- **Sandbox testing is part of the acceptance flow** — the accepted-submission field on handling programme updates (§6.1, "JSON update handling") should point teams at `sandbox` as the way to test it before the conference (no live-changing sandbox feed exists; entrants exercise their update logic by manually re-fetching after a change is published).
- **Licence: CC BY-NC-SA 4.0** on the programme data (attribution, non-commercial, share-alike on derived *data*, not on app source code). A `LICENCE` file must ship at `/data/LICENCE`, and `licence`/`licence_url` fields must appear in every feed's top-level metadata. This licence is separate from, and does not require, the open-source licence on the competition entry's own codebase (§5.3).
- **No attendee/personal data is provided by the feed**, and none is required to build a compliant entry — the spec frames "don't collect personal data" as the simplest path through the data protection hurdle (§8, "data protection requirements"). Personalisation is expected to be client-side/local only (in-memory or `localStorage`).
- **Path collision to resolve at build time:** if the documentation page is served at `/data`, it must not collide with the `/data/` feed directory. Either serve the page at `/data/` and feeds beneath it, or move the page to `/programme-data` and keep `/data/` purely for files — pick one and be explicit in the implementation.
- **Hosting is GitHub Pages** with non-configurable caching (`Cache-Control: max-age=600`) and default CORS (`Access-Control-Allow-Origin: *`); confirm cross-origin fetch works from a third-party domain as part of the launch checklist (see the launch checklist in [CHI_Programme_Data_Website_Content.md](CHI_Programme_Data_Website_Content.md) §B4, which should be merged into this site's overall pre-launch checklist).
- **The published feed's actual schema is the conference system's native export, documented in the data spec's Part C** (`schemeVersion: 7`: camelCase field names, epoch-millisecond dates, `sessions`/`events`/`contents`/`people`/`rooms`/`tracks`/… as shown there) — this is published as-is, with no reshaping into the `edition`/`revision`/snake_case/`status`/`last_modified` shape sketched in Part A. **Part A's page copy and code sample are illustrative of intent, not a description of the real, current schema**, and need rewriting before publication to describe the Part C shape accurately (including that there is currently no `status`, `status_note`, or `last_modified` field, and no soft-delete guarantee, since the raw export carries none of those). Do not build the "What's in the file" section, the JSON Schema at `/data/schema/v1.json`, or the update-detection code sample from Part A's sketch — base them on Part C. Flag this discrepancy to the chairs rather than silently reconciling it, since it affects what update-detection strategy entrants can actually rely on (e.g. `publicationInfo.version` may be the real analogue of "revision", not a top-level `revision` field).

### Judging — acceptance hurdles (pass/fail)

All submissions must meet these to be listed. Not scored.

- **Open source** — codebase publicly available under an open source licence.
- **Security** — no obvious security vulnerabilities; jury may exclude unacceptable risk.
- **Data protection** — accepted teams receive CHI's data protection requirements and must confirm compliance before listing; initial submissions demonstrate intent to comply. *(Note: the detailed data protection requirements are still to be finalised — see §8.)*

### Judging — scored criteria

| Criterion | Weight |
|---|---|
| User Experience | 25% |
| Novelty & Creativity | 25% |
| Inclusion & Accessibility | 25% |
| Relevance to CHI Use Cases | 15% |
| Technical Execution | 10% |

### Awards

In addition to the highlighted-app selection, the jury gives **category awards** (e.g. best user experience, most innovative, best for inclusion & accessibility; final categories TBC). Awards are recognition/certificate only and are announced live at CHI 2027. Represent these on the Judging page.

---

## 5. Initial submission form

The **initial submission is a prototype / proof of concept** — set that expectation clearly on the form. Group fields into the sections below. Required unless marked optional.

### 5.1 About your team

| Field | Type | Notes |
|---|---|---|
| Team name | text | |
| Lead contact name | text | |
| Lead contact email | email | Used for all correspondence |
| Team members | repeatable text | Name + affiliation per member |
| CHI conflict of interest | yes/no | Are any team members CHI authors or programme committee members? |

### 5.2 About your app

| Field | Type | Notes |
|---|---|---|
| App name | text | |
| App icon | file upload | Square image, min 512×512px; PNG/JPG |
| Tagline | text | Max 80 characters |
| One-line description | text | Max 150 characters |
| Full description | textarea | Max 500 words; "what does it do, and why does it matter?" |
| Target attendee persona(s) | multi-select | e.g. first-timer, paper author, industry attendee, accessibility needs; allow "other" |
| When is it relevant? | multi-select | Before / During / After the event |
| Demo URL or downloadable build | URL / file | Must be accessible to the jury; include access instructions |
| Example login or guest access | textarea | Optional; if applicable |
| Walkthrough video URL | URL | Max 5 minutes; screen recording acceptable |

### 5.3 Technical and legal

| Field | Type | Notes |
|---|---|---|
| Public source code repository URL | URL | Must be open source |
| Open source licence | select / text | e.g. MIT, Apache 2.0, GPL |
| Third-party libraries, APIs, or AI tools used | textarea | List all, including AI-generated components |
| IP ownership confirmation | checkbox | "We confirm our team owns or has rights to all components of this submission" |
| Data handling declaration | textarea | What personal data (if any) does the app collect or process? |
| Data protection intent | checkbox | "We commit to complying with the CHI data protection requirements shared upon acceptance" |

### 5.4 Optional (strengthens the application)

| Field | Type | Notes |
|---|---|---|
| Accessibility features | textarea | Implemented or planned |
| LLM / AI component details | textarea | How used, and the user-facing behaviour |
| Evidence of user testing | textarea | Early feedback / testing notes |
| Anything else for the jury | textarea | Free text |

---

## 6. Accepted submission form

Shown only to accepted teams (after the end-of-January 2027 notification). Can be a gated page or a separate form released at that stage. Due Friday 26 March 2027.

### 6.1 Technical

| Field | Type | Notes |
|---|---|---|
| Production build URL | URL | Fully functional, integrated with the live CHI 2027 programme feed at `chidigitalexperience.org/data/chi2027/latest.json` |
| JSON update handling | textarea | How the app receives/reflects programme updates during the event |
| Scaling plan | textarea | How the app handles conference-scale concurrent usage; hosting + any load testing |
| Security confirmation | checkbox | "We confirm the app has been reviewed for common security vulnerabilities" |
| Incident contact | text | Name + email reachable during the conference |
| Backup contact | text | Name + email |

### 6.2 Submission package

| Field | Type | Notes |
|---|---|---|
| Updated walkthrough video URL | URL | Reflecting changes since initial submission; max 5 min |
| One-page summary | file / textarea | For publication on CHI site and materials; app name, description, use case(s), team names + affiliations |
| Signed consent form | file upload | Template provided; covers data use, promotion, IP acknowledgement; from all members |
| Showcase participation | acknowledgement | Accepted teams invited to demo at the CHI 2027 showcase; format/scheduling confirmed later |

### 6.3 Data and privacy

| Field | Type | Notes |
|---|---|---|
| Completed privacy checklist | file / form | Template provided on acceptance |
| Consent flow confirmation | checkbox / textarea | If collecting attendee data: confirm consent flows meet CHI data protection requirements |
| Data retention confirmation | checkbox | "We confirm no attendee data will be retained beyond 30 days post-event without explicit opt-in" |

### 6.4 Ongoing obligations (acknowledge at submission)

Render as required checkboxes:

- Available during the conference for a brief jury walkthrough session
- Will participate in the post-event retrospective with Programme Innovation Chairs
- Will disclose any significant post-acceptance changes before deployment

---

## 7. Functional requirements

- **Form submission handling** — persist submissions to a datastore; email a confirmation to the lead contact on submit; email/notify chairs on new submission.
- **File uploads** — support the icon, and any file-based fields (consent form, one-page summary). Enforce type/size limits. Store securely.
- **Save & resume** *(nice to have)* — let applicants save a draft and return. If out of scope for v1, allow the form to be completed in one sitting but make length manageable.
- **Deadline enforcement** — close the initial form after the prototype deadline; gate the accepted form to the accepted window.
- **Admin view** — a simple authenticated view for chairs to list, read, and **export (CSV/JSON)** all submissions, including links to uploaded files.
- **FAQ management** — chairs should be able to edit FAQ content without a code deploy (CMS, markdown file, or simple editable data source).
- **Data download & API docs** — the historical JSON is a documented download; the API documentation is a static, versioned page.

---

## 8. Deferred / to be supplied

These are not yet finalised and should be built as clearly-marked placeholders that are easy to populate later:

- **Data protection requirements** — the detailed requirements shared with accepted teams. Referenced by the acceptance hurdle and several form fields. **Do not invent content**; leave a placeholder and a single source of truth to fill in.
- **Consent form template**, **privacy checklist template**, **one-page summary template** — referenced by the accepted form.
- **Compute/LLM credits detail** — pending sponsorship.
- ~~**Historical JSON data file and schema** — to be supplied by the chairs.~~ **Resolved** — fully specified in [CHI_Programme_Data_Website_Content.md](CHI_Programme_Data_Website_Content.md): feed structure, schema location (`/data/schema/v1.json`), collections, and the CHI 2025/2026/sandbox datasets.
- ~~**Live API endpoint + auth**~~ **Resolved — no auth.** There is no keyed API; the live CHI 2027 feed is a public, unauthenticated static file at the same path as the historical feeds, published from April 2027. See §4a.
- **Two open licensing questions** flagged in the data spec (§B6 there) still need chair/legal sign-off before launch: whether *NonCommercial* is meant to exclude industry entrants and how that interacts with a free-but-commercial app, and whether CHI/ACM holds the rights to license paper abstracts under CC BY-NC-SA as distinct from schedule facts. A short FAQ line can resolve most of the first.

---

## 9. Non-functional requirements

- **Accessibility is a first-class requirement.** This is a CHI competition and one of the judging criteria is inclusion & accessibility — the site itself must model best practice. Target WCAG 2.2 AA: full keyboard operability, sensible focus order, labelled form fields with clear error messaging, sufficient contrast, respects reduced-motion, works with screen readers.
- **Mobile-first and responsive.** Forms must be comfortable to complete on a phone.
- **Performant and low-maintenance** — this runs for ~a year with occasional content edits; prefer a simple, robust stack over anything heavy.
- **Secure** — validate and sanitise all input; protect uploads and the admin view; no secrets in the client.
- **Privacy-respecting** — collect only what the forms specify; be mindful that applicant data is personal data.

---

## 10. Suggested approach

Stack is open, but a good fit would be: a static or lightly-server-rendered site for content pages, with a small backend (or a serverless form handler) for submissions, file storage, and the admin export. Keep content (dates, criteria, FAQ) in editable data files or a lightweight CMS so the chairs can update without a developer. Prioritise the applicant-facing flow and the initial submission form for v1; the accepted-stage form and admin export can follow before the end-of-January 2027 notification.

---

*Source of truth for competition content: the "CHI Programme Innovation — Chair Planning Materials" document. Source of truth for the Programme Data page and feed build: [CHI_Programme_Data_Website_Content.md](CHI_Programme_Data_Website_Content.md). Where this spec and either of those documents differ, confirm with the chairs.*
