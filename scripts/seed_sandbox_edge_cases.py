#!/usr/bin/env python3
"""
Inject deliberately awkward edge cases into a copy of real programme data,
producing the sandbox dataset described in spec/CHI_Programme_Data_Spec.md §5.

All mutations use only fields that already exist in the real QOALA export
schema (schemeVersion 7) — no invented fields. New records get synthetic IDs
above the existing maximum in their collection so they never collide with
real ones.

Usage:
    scripts/seed_sandbox_edge_cases.py <source-json> <output-json>

Example:
    scripts/seed_sandbox_edge_cases.py test_data/CHI_2025_program.json /tmp/sandbox_seeded.json
    scripts/publish.py sandbox /tmp/sandbox_seeded.json -m "Rebuild sandbox with edge cases"
"""
import argparse
import copy
import json
import sys
from pathlib import Path

DAY_MS = 24 * 60 * 60 * 1000
HOUR_MS = 60 * 60 * 1000
MIN_MS = 60 * 1000


def next_id(items: list[dict]) -> int:
    return max((item["id"] for item in items), default=0) + 1


def make_id_pool(data: dict, collection: str, start_at: int = 900000):
    """Return a counter starting well above real IDs, for deterministic synthetic records."""
    current_max = next_id(data.get(collection, [])) - 1
    return max(current_max + 1, start_at)


def add_edge_cases(data: dict) -> dict:
    data = copy.deepcopy(data)

    rooms = data["rooms"]
    tracks = data["tracks"]
    time_slots = data["timeSlots"]
    sessions = data["sessions"]
    contents = data["contents"]
    people = data["people"]

    room_id_ctr = make_id_pool(data, "rooms")
    track_id_ctr = make_id_pool(data, "tracks")
    slot_id_ctr = make_id_pool(data, "timeSlots")
    session_id_ctr = make_id_pool(data, "sessions")
    content_id_ctr = make_id_pool(data, "contents")
    person_id_ctr = make_id_pool(data, "people")

    conf_start = data["conference"]["startDate"]
    default_room_id = rooms[0]["id"]
    default_track_id = tracks[0]["id"] if tracks else None
    default_type_id = sessions[0]["typeId"] if sessions else None

    def new_person(**kwargs) -> dict:
        nonlocal person_id_ctr
        p = {
            "id": person_id_ctr,
            "firstName": "",
            "lastName": "",
            "middleInitial": "",
            "importedId": f"sandbox-person-{person_id_ctr}",
            "source": "SANDBOX",
            "affiliations": [],
        }
        p.update(kwargs)
        person_id_ctr += 1
        people.append(p)
        return p

    def new_time_slot(start_offset_ms: int, duration_ms: int, slot_type: str = "SESSION") -> dict:
        nonlocal slot_id_ctr
        ts = {
            "id": slot_id_ctr,
            "type": slot_type,
            "startDate": conf_start + start_offset_ms,
            "endDate": conf_start + start_offset_ms + duration_ms,
        }
        slot_id_ctr += 1
        time_slots.append(ts)
        return ts

    def new_content(**kwargs) -> dict:
        nonlocal content_id_ctr
        c = {
            "id": content_id_ctr,
            "typeId": contents[0]["typeId"] if contents else None,
            "title": "Untitled",
            "addons": {},
            "recognitionIds": [],
            "isBreak": False,
            "importedId": f"sandbox-content-{content_id_ctr}",
            "source": "SANDBOX",
            "trackId": default_track_id,
            "tags": [],
            "keywords": [],
            "sessionIds": [],
            "eventIds": [],
            "abstract": "",
            "authors": [],
        }
        c.update(kwargs)
        content_id_ctr += 1
        contents.append(c)
        return c

    def new_session(**kwargs) -> dict:
        nonlocal session_id_ctr
        s = {
            "id": session_id_ctr,
            "name": "Untitled Session",
            "addons": {},
            "isParallelPresentation": False,
            "importedId": f"sandbox-session-{session_id_ctr}",
            "typeId": default_type_id,
            "roomId": default_room_id,
            "chairIds": [],
            "contentIds": [],
            "source": "SANDBOX",
            "timeSlotId": None,
        }
        s.update(kwargs)
        session_id_ctr += 1
        sessions.append(s)
        return s

    # --- 1. A contribution with 40+ authors -------------------------------
    many_authors = []
    for i in range(45):
        p = new_person(firstName=f"Author{i:02d}", lastName="MultiAuthorTest")
        many_authors.append({
            "personId": p["id"],
            "affiliations": [{
                "institution": f"Institution {i % 7}",
                "dsl": "Dept. of Everything",
                "city": "Nowhere",
                "state": "",
                "country": "Testland",
            }],
        })
    slot = new_time_slot(3 * DAY_MS + 10 * HOUR_MS, 80 * MIN_MS)
    content = new_content(
        title="A Paper With An Implausible Number Of Authors",
        abstract="This contribution exists to test author-list rendering at scale.",
        authors=many_authors,
    )
    session = new_session(name="Massive Collaboration Showcase", timeSlotId=slot["id"], contentIds=[content["id"]])
    content["sessionIds"] = [session["id"]]

    # --- 2. Emoji, CJK, RTL text and combining diacritics in titles/names -
    weird_scripts_person = new_person(
        firstName="مُحَمَّد", lastName="山田太郎",
        affiliations=[{"institution": "🏫 Ünïvërsïty of Ｗëird Ｔëxt", "dsl": "", "city": "東京", "state": "", "country": "日本"}],
    )
    slot = new_time_slot(3 * DAY_MS + 11 * HOUR_MS + 40 * MIN_MS, 20 * MIN_MS)
    content = new_content(
        title="🎉 テスト тест اختبار Test — é́́ combining diacritics stress",
        abstract="مرحبا بالعالم — 你好世界 — こんにちは世界 — Здравствуй, мир — שלום עולם. RTL and CJK mixed with emoji 🚀🔥.",
        authors=[{"personId": weird_scripts_person["id"], "affiliations": []}],
    )
    session = new_session(name="国際化 Internationalization ﻿& Text Rendering Session", timeSlotId=slot["id"], contentIds=[content["id"]])
    content["sessionIds"] = [session["id"]]

    # --- 3. A 4,000-character abstract, and a six-word one ----------------
    long_abstract = ("This abstract is deliberately long to test truncation, scrolling, and "
                      "layout behaviour in client applications. ")
    long_abstract = (long_abstract * (4000 // len(long_abstract) + 1))[:4000]
    slot = new_time_slot(3 * DAY_MS + 12 * HOUR_MS + 10 * MIN_MS, 20 * MIN_MS)
    content = new_content(title="The Extremely Long Abstract Paper", abstract=long_abstract)
    session = new_session(name="Long Abstract Test Session", timeSlotId=slot["id"], contentIds=[content["id"]])
    content["sessionIds"] = [session["id"]]

    slot = new_time_slot(3 * DAY_MS + 12 * HOUR_MS + 40 * MIN_MS, 20 * MIN_MS)
    content = new_content(title="The Extremely Short Abstract Paper", abstract="Six words exactly in this line.")
    session = new_session(name="Short Abstract Test Session", timeSlotId=slot["id"], contentIds=[content["id"]])
    content["sessionIds"] = [session["id"]]

    # --- 4. LaTeX fragments and HTML entities in titles --------------------
    slot = new_time_slot(3 * DAY_MS + 13 * HOUR_MS + 10 * MIN_MS, 20 * MIN_MS)
    content = new_content(
        title="On $O(n \\log n)$ Complexity &amp; the &lt;Sorting&gt; Problem \\alpha \\beta \\sum_{i=1}^{n}",
        abstract="Contains raw LaTeX: $E = mc^2$, \\textbf{bold}, and HTML entities: &copy; &nbsp; &mdash; &quot;quoted&quot;.",
    )
    session = new_session(name="Markup & Escaping Stress Test", timeSlotId=slot["id"], contentIds=[content["id"]])
    content["sessionIds"] = [session["id"]]

    # --- 5. A session with no room assigned yet (roomId: null), tba-like --
    slot = new_time_slot(3 * DAY_MS + 14 * HOUR_MS, 60 * MIN_MS)
    content = new_content(title="Room To Be Announced Panel", abstract="Venue not yet confirmed.")
    session = new_session(name="TBA Room Panel", roomId=None, timeSlotId=slot["id"], contentIds=[content["id"]])
    content["sessionIds"] = [session["id"]]

    # --- 6. Two sessions overlapping in the same room ----------------------
    overlap_room = rooms[1]["id"] if len(rooms) > 1 else default_room_id
    slot_a = new_time_slot(3 * DAY_MS + 15 * HOUR_MS, 60 * MIN_MS)
    slot_b = new_time_slot(3 * DAY_MS + 15 * HOUR_MS + 30 * MIN_MS, 60 * MIN_MS)
    content_a = new_content(title="Overlap Session A", abstract="First of two sessions double-booked into the same room.")
    session_a = new_session(name="Double-Booked Session A", roomId=overlap_room, timeSlotId=slot_a["id"], contentIds=[content_a["id"]])
    content_a["sessionIds"] = [session_a["id"]]
    content_b = new_content(title="Overlap Session B", abstract="Second of two sessions double-booked into the same room.")
    session_b = new_session(name="Double-Booked Session B", roomId=overlap_room, timeSlotId=slot_b["id"], contentIds=[content_b["id"]])
    content_b["sessionIds"] = [session_b["id"]]

    # --- 7. A 7am session ----------------------------------------------------
    slot = new_time_slot(4 * DAY_MS + 7 * HOUR_MS, 45 * MIN_MS)
    content = new_content(title="Sunrise Yoga and HCI Reflections", abstract="An unusually early session.")
    session = new_session(name="07:00 Early Session", timeSlotId=slot["id"], contentIds=[content["id"]])
    content["sessionIds"] = [session["id"]]

    # --- 8. A session crossing midnight --------------------------------------
    slot = new_time_slot(4 * DAY_MS + 23 * HOUR_MS + 30 * MIN_MS, 90 * MIN_MS)  # 23:30 -> 01:00 next day
    content = new_content(title="Late-Night Demo Session", abstract="Crosses midnight into the following conference day.")
    session = new_session(name="Midnight-Crossing Demo Session", timeSlotId=slot["id"], contentIds=[content["id"]])
    content["sessionIds"] = [session["id"]]

    # --- 9. Nulls in every optional field -----------------------------------
    null_person = new_person(
        firstName="Null", lastName="Fields",
        middleInitial=None, importedId=None, affiliations=[],
    )
    slot = new_time_slot(5 * DAY_MS + 9 * HOUR_MS, 30 * MIN_MS)
    content = new_content(
        title="All Optional Fields Null",
        abstract=None,
        trackId=None,
        tags=None,
        keywords=None,
        authors=[{"personId": null_person["id"], "affiliations": None}],
    )
    session = new_session(
        name="Null Fields Session",
        roomId=None,
        chairIds=None,
        timeSlotId=slot["id"],
        contentIds=[content["id"]],
    )
    content["sessionIds"] = [session["id"]]

    # --- 10. A cancelled session (marked via addons; no status field exists
    #         in this schema, so we use the same addons dict real data uses
    #         for out-of-band metadata) ----------------------------------
    slot = new_time_slot(5 * DAY_MS + 10 * HOUR_MS, 60 * MIN_MS)
    content = new_content(title="Cancelled Session Placeholder", abstract="This session's talk was withdrawn.")
    session = new_session(
        name="[CANCELLED] Withdrawn Talk Session",
        timeSlotId=slot["id"],
        contentIds=[content["id"]],
        addons={"cancelled": True, "cancelledReason": "Speaker withdrew"},
    )
    content["sessionIds"] = [session["id"]]

    # --- 11. A relocated session (roomId differs from its originally
    #         published room, recorded via addons.relocatedFrom) --------
    original_room = rooms[2]["id"] if len(rooms) > 2 else default_room_id
    new_room = rooms[3]["id"] if len(rooms) > 3 else default_room_id
    slot = new_time_slot(5 * DAY_MS + 11 * HOUR_MS, 60 * MIN_MS)
    content = new_content(title="Relocated Session Paper", abstract="Moved rooms after initial publication.")
    session = new_session(
        name="Relocated Session",
        roomId=new_room,
        timeSlotId=slot["id"],
        contentIds=[content["id"]],
        addons={"relocatedFrom": original_room, "relocatedReason": "Capacity"},
    )
    content["sessionIds"] = [session["id"]]

    # --- 12. A session rescheduled twice (addons carries reschedule history) -
    slot = new_time_slot(5 * DAY_MS + 13 * HOUR_MS, 60 * MIN_MS)
    original_slot_1 = conf_start + 2 * DAY_MS + 9 * HOUR_MS
    original_slot_2 = conf_start + 3 * DAY_MS + 16 * HOUR_MS
    content = new_content(title="Twice-Rescheduled Session Paper", abstract="Moved time slots twice before the final schedule.")
    session = new_session(
        name="Rescheduled Twice Session",
        timeSlotId=slot["id"],
        contentIds=[content["id"]],
        addons={"rescheduleHistory": [original_slot_1, original_slot_2]},
    )
    content["sessionIds"] = [session["id"]]

    # --- Extra: a room with zero capacity and a room with an absurdly large one,
    #     to catch capacity-based layout assumptions --------------------------
    rooms.append({"id": room_id_ctr, "name": "Broom Closet (Overflow)", "setup": "SPECIAL", "typeId": rooms[0]["typeId"], "capacity": 0})
    room_id_ctr += 1
    rooms.append({"id": room_id_ctr, "name": "Stadium Plenary Hall", "setup": "SPECIAL", "typeId": rooms[0]["typeId"], "capacity": 100000})
    room_id_ctr += 1

    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", type=Path, help="path to a real programme JSON file to base the sandbox on")
    parser.add_argument("output", type=Path, help="where to write the seeded sandbox JSON")
    args = parser.parse_args()

    if not args.source.exists():
        sys.exit(f"error: source file not found: {args.source}")

    with args.source.open("r", encoding="utf-8") as f:
        data = json.load(f)

    seeded = add_edge_cases(data)

    with args.output.open("w", encoding="utf-8") as f:
        json.dump(seeded, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Wrote seeded sandbox data to {args.output}")
    print(f"  sessions: {len(seeded['sessions'])}  contents: {len(seeded['contents'])}  people: {len(seeded['people'])}  rooms: {len(seeded['rooms'])}")


if __name__ == "__main__":
    main()
