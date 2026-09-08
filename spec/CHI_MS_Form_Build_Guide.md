# CHI 2027 Programme Innovation — Microsoft Forms Build Guide

*Initial submission form. Everything below is copy-and-paste ready: question text goes in the question title, subtitle text goes in the "Subtitle" field (click the **…** menu on a question → Subtitle).*

---

## Part A — Read this first: four MS Forms constraints that change the design

These are limitations of the platform, not choices. Each one has a recommended workaround baked into Part C.

**1. File upload forces respondents to sign in, so the form collects no files at all.**
The "File upload" question type only appears when the form is restricted to your organisation or respondents sign in with a Microsoft account. Since entrants are external developers worldwide, the form must be set to "Anyone can respond" — and that question type disappears.

> This turns out not to matter. Every submission is open source, so the two things the judges actually need are both URLs: **the running application** and **the public git repository**. The icon lives in the repository too, so it's a link like everything else — no file uploads anywhere in the form.

**2. There is no character or word limit enforcement.**
MS Forms can restrict *numeric* answers to a range, but cannot cap the length of a text answer. All the "max 80 characters" style limits have to be stated in the subtitle and checked by you at triage.

> *Recommendation:* keep the limits in the wording as a clear instruction, and add a line to the form intro saying over-length answers may be trimmed for promotional use. That way you have licence to cut without a back-and-forth.

**3. There are no repeatable fields.**
Team members can't be an "add another member" block, so the list is one long-answer question with the required format spelled out in the subtitle. Wording in Q4. It means you'll be parsing free text rather than tidy rows — acceptable for conflict checking, less so if you ever want per-member data.

**4. Save-and-resume only works for signed-in respondents.**
Anonymous respondents lose everything if they close the tab.

> *Recommendation:* publish the full question list as a page on chidigitalexperience.org so entrants can prepare their answers offline before opening the form. This is worth doing regardless — it also lets teams see the requirements before committing.

---

## Part B — What you need to create

A checklist of the build, in order:

1. **A "Prepare your submission" page** on chidigitalexperience.org listing all questions (see constraint 4)
2. **The form itself** — 5 sections, 24 questions (Part C)
3. **Form settings** — response window, notifications, thank-you message (Part D)
4. **A confirmation email mechanism** — MS Forms cannot email an anonymous respondent a receipt. Either a Power Automate flow triggered on new response, or accept that the on-screen thank-you message is the only confirmation. Wording for both in Part D.
5. **A results destination** — the linked Excel workbook, plus a decision on where files/links get archived
6. **A test pass** — submit twice yourself from a private browser window before launch

---

## Part C — The form

### Form title

```
CHI 2027 Programme Innovation — Initial Submission
```

### Form description

```
Thank you for entering. This form is for your initial submission: a prototype or proof of concept, not a finished product. We are evaluating your idea and your approach, so please don't let polish get in the way of a strong concept.

Before you start:
• You cannot save and return to this form, so please prepare your answers first. The full question list is at chidigitalexperience.org.
• You will need a working demo link, a walkthrough video link, and a public code repository URL.
• Deadline: Friday 4 December 2026.
• Questions: app@chi2027.acm.org
```

---

### Section 1 — Your team

*Section description:*
```
We'll use the lead contact for all correspondence about your submission. We also need to know who's on your team so we can assign judges without a conflict of interest.
```

**Q1 — Team name**
- Type: Text (single line) · Required
- Subtitle: `The name you'd like us to use for your team in any published materials.`

**Q2 — Lead contact name**
- Type: Text (single line) · Required
- Subtitle: *(none)*

**Q3 — Lead contact email**
- Type: Text (single line) · Required · Restrictions: *Email*
- Subtitle: `All correspondence about your submission will go to this address. Please make sure it's one you check.`

**Q4 — All team members**
- Type: Text (long answer) · Required
- Subtitle: `One person per line, in the format: Name — Affiliation. Include the lead contact, and list everyone who has worked on the submission. Affiliation can be a university, company, or "independent". We use this to check for conflicts of interest when assigning judges — an incomplete list risks your submission going to a judge who shouldn't be reviewing it.`

**Q5 — Country or region the team is based in**
- Type: Text (single line) · Required
- Subtitle: `Free text. We use this only to understand the reach of the competition.`

**Q6 — Are any team members CHI 2027 authors, committee members, or organisers?**
- Type: Choice (single) · Required
- Options:
  - `Yes`
  - `No`
- Subtitle: `This is a conflict-of-interest declaration only. Saying yes does not affect your eligibility — it just means we'll assign judges accordingly.`

**Q7 — If yes, please give details**
- Type: Text (long answer) · Not required
- Subtitle: `Which team members, and in what role.`
- *Branching:* set Q6 → `Yes` goes to Q7; `No` skips to Section 2.

---

### Section 2 — Your app

*Section description:*
```
Tell us what you've built and who it's for.
```

**Q8 — App name**
- Type: Text (single line) · Required
- Subtitle: `The name you want used in public listings and promotional material.`

**Q9 — Link to your app icon**
- Type: Text (single line) · Required · Restrictions: *Url*
- Subtitle: `A square image, minimum 512×512px, PNG or JPG. Commit it to your repository and paste the direct link to the file here. We'll use this in listings, signage, and promotional material, so please make sure it's the version you want the world to see.`

**Q10 — Tagline**
- Type: Text (single line) · Required
- Subtitle: `One short phrase, maximum 80 characters. This is what appears next to your app name on signage and in listings. Over-length taglines may be trimmed.`

**Q11 — One-line description**
- Type: Text (single line) · Required
- Subtitle: `Maximum 150 characters. A single sentence explaining what your app does, written for an attendee who has never heard of it.`

**Q12 — Full description**
- Type: Text (long answer) · Required
- Subtitle: `Maximum 500 words. What does it do, and why does it matter? Tell us what problem or opportunity you saw in the CHI attendee experience, and how your app responds to it.`

**Q13 — Which attendees is this for?**
- Type: Choice (multiple answers) · Required · "Other" option enabled
- Subtitle: `Select all that apply.`
- Options:
  - `First-time attendees`
  - `Returning attendees`
  - `Paper or contribution authors`
  - `Students`
  - `Industry practitioners`
  - `Academic researchers`
  - `Attendees with accessibility needs`
  - `Attendees joining remotely or in a hybrid capacity`
  - `Student volunteers, organisers, or committee members`
  - `Other`

---

### Section 3 — Your app and your code

*Section description:*
```
Two links do most of the work in this competition: somewhere the judges can use your app, and the public repository holding the code behind it. Both must be openly accessible — no logins, no invitations — and must stay live until at least the end of January 2027.
```

**Q14 — URL of your working app**
- Type: Text (single line) · Required · Restrictions: *Url*
- Subtitle: `A live, public URL the judges can open and use straight away, with no login, account creation, or invitation required. It's fine if it's rough or partly incomplete — this is a prototype. Please keep it accessible throughout the judging period. If your app genuinely cannot be a URL, paste a download link instead.`

**Q15 — URL of your public git repository**
- Type: Text (single line) · Required · Restrictions: *Url*
- Subtitle: `The repository holding the code behind the app above. It must be public and viewable without a login — GitHub, GitLab, Codeberg, or anywhere equivalent. Open source is a pass/fail requirement for this competition, so a private or missing repository means we can't consider your submission.`

**Q16 — Open source licence**
- Type: Choice (single) · Required · "Other" option enabled
- Subtitle: `The licence in your repository. If you haven't added one yet, add one before you submit — a repository with no licence is not open source by default.`
- Options:
  - `MIT`
  - `Apache 2.0`
  - `BSD (2- or 3-clause)`
  - `GPL v3`
  - `AGPL v3`
  - `Mozilla Public License 2.0`
  - `Other`

**Q17 — Walkthrough video link**
- Type: Text (single line) · Required · Restrictions: *Url*
- Subtitle: `Maximum 5 minutes. A screen recording with narration is completely fine — no production value expected. Walk us through what the experience is, who it's for, and what makes it interesting. Host it anywhere the judges can watch without an account (YouTube unlisted, Vimeo, or a direct file link).`

---

### Section 4 — Technical and legal

*Section description:*
```
A short section so we understand what your prototype is built on and how it handles data.
```

> *Note:* the security confirmation sits on the accepted-stage form rather than here. The intellectual property and data protection confirmations are on this form, at Q20 and Q21.

**Q18 — Third-party libraries, APIs, models, and AI tools used**
- Type: Text (long answer) · Required
- Subtitle: `List everything you've built on top of, including any AI tools used to generate code or content. We're not judging you for using them — vibe coding is welcome — we just need an accurate picture of what's in the stack.`

**Q19 — What personal data does your app collect or process?**
- Type: Text (long answer) · Required
- Subtitle: `Be specific: what data, from whom, where it's stored, and how long it's kept. If your app collects no personal data at all, write "none" — that's a perfectly good answer and often the strongest one.`

**Q20 — Intellectual property**
- Type: Choice (multiple answers) · Required
- Subtitle: `Please confirm the following.`
- Options:
  - `We confirm our team owns or has the rights to all components of this submission, and that all third-party components are acknowledged above.`

**Q21 — Data protection**
- Type: Choice (multiple answers) · Required
- Subtitle: `Accepted teams will receive CHI's data protection requirements in full and must confirm compliance before their app is listed or promoted.`
- Options:
  - `We commit to complying with the CHI data protection requirements shared with us on acceptance.`

> *Note:* the detailed requirements are still to be finalised, so Q21 is deliberately worded as a forward commitment — it can go live without them. Two things follow from that: the phrase "shared with us on acceptance" is doing real work, so make sure the requirements genuinely are sent at acceptance and not later; and because a tick box is not a substitute for the requirements themselves, the accepted-stage form still needs a confirmation against the finalised text.

---

### Section 5 — Optional extras

*Section description:*
```
Nothing in this section is required, but each of these helps the judges understand your work. Inclusion and accessibility is one of our highest-weighted criteria, so the first question is worth your time.
```

**Q22 — Accessibility features**
- Type: Text (long answer) · Not required
- Subtitle: `What have you implemented, and what's planned? Keyboard operability, screen reader support, contrast, language support, reduced motion — whatever applies. Honest "planned but not built yet" answers are useful to us.`

**Q23 — LLM or AI components**
- Type: Text (long answer) · Not required
- Subtitle: `If your app uses a model at runtime, tell us which one, what it does, and what the user sees. Include how you handle failure or unexpected output.`

**Q24 — Anything else the judges should know**
- Type: Text (long answer) · Not required
- Subtitle: `Free text. Use this for context that doesn't fit anywhere else — including anything about your demo, such as which parts are functional and which are mocked up.`

---

## Part D — Settings and messages

### Response settings

| Setting | Value |
|---|---|
| Who can respond | **Anyone can respond** (entrants are external) |
| Accept responses | On, with a **start date** of your launch date and an **end date** of 4 December 2026 |
| Record name | Off |
| One response per person | Off |
| Shuffle questions | Off |
| Get email notification of each response | **On**, so submissions don't sit unnoticed |

> **Two things to check on the deadline.** MS Forms closes the form using *your* tenant's timezone, not the respondent's. If you intend the deadline to be generous — end of day anywhere in the world — set the end date to close at the equivalent of 4 December 23:59 in the last timezone (UTC−12), which is 5 December 11:59 UTC. State the intended deadline explicitly in the form description and on the website so nobody has to work it out.

### Thank-you message

Settings → Customise thank you message:

```
Your submission has been received. Thank you for entering.

What happens next: we'll review all submissions against the acceptance requirements and the judging criteria, and you'll hear from us by the end of January 2027. Please keep your demo and video links live until then.

We have not sent you a copy of your answers, so if you'd like a record, take a screenshot of this page or note down what you submitted.

If you need to correct something, or if anything changes, email app@chi2027.acm.org with your team name in the subject line.
```

*If you build the Power Automate confirmation flow instead, replace the third paragraph with:* `A confirmation has been sent to your lead contact email address.`

### Confirmation email (if using Power Automate)

Trigger: *When a new response is submitted* → *Get response details* → *Send an email (V2)* to the Q3 answer.

Subject:
```
CHI 2027 Programme Innovation — submission received
```

Body:
```
Hello,

We've received your initial submission to the CHI 2027 Programme Innovation competition. Thank you for entering.

Team name: [Q1 answer]
App name: [Q8 answer]
Submitted: [submission timestamp]

You'll hear from us by the end of January 2027. In the meantime, please keep your demo and walkthrough video links live and accessible — the judges will need them.

If anything changes, or you spot a mistake in your submission, reply to this address and tell us your team name.

The CHI 2027 Programme Innovation Chairs
app@chi2027.acm.org
```

---

## Part E — Open questions for you and your co-chair

1. **Are multiple submissions per team allowed?** The form as written doesn't stop it. If you want one entry per team, say so in the description; if you're happy to allow several, nothing changes.
2. **Q5 (country/region)** — I've included it as light demographic data for reporting on the competition's reach. Drop it if you'd rather not collect anything you don't need.
3. **Will you let accepted teams replace the icon before promotion?** Collecting it at Q9 means you have promotional material from day one, but a prototype-stage icon may not be what a team wants on conference signage. Saying explicitly that it can be updated at the accepted stage costs you nothing and avoids teams over-thinking it now.
4. **Only the security confirmation is now deferred to the accepted-stage form,** which already has one. Worth a quick check that the IP wording at Q20 and the consent form template don't contradict each other — the template covers IP acknowledgement too, and two differently worded confirmations of the same thing is the sort of detail that surfaces at exactly the wrong moment.
5. **Do you want to check the repository actually builds?** Right now Q15 collects the URL and the judges see the code, but nothing asks whether a third party can run it. A short optional question — or a README requirement — would tell you whether "open source" means genuinely reusable or just publicly readable. Worth deciding before launch, because it's hard to add fairly once entries are in.
