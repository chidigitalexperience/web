#!/usr/bin/env python3
"""
Publish a new CHI programme JSON file into the data/ directory structure.

Usage:
    scripts/publish.py <edition> <path-to-new-json> [--message "what changed"] [--force]

Example:
    scripts/publish.py chi2027 ~/Downloads/CHI_2027_program.json -m "Room change for s-0388"

Implements the publish sequence from spec/CHI_Programme_Data_Spec.md §7.2:
  1. Validate the incoming file
  2. Increment revision, stamp generated_at is left to the source file as-is
     (the file's own content is trusted; we only add revision bookkeeping)
  3. Write data/<edition>/revisions/NNN.json
  4. Copy to data/<edition>/latest.json
  5. Write data/<edition>/version.json

Does not commit or push — do that yourself once you're happy with `git diff`.
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DATA_ROOT = Path(__file__).resolve().parent.parent / "public" / "data"

REQUIRED_TOP_LEVEL_KEYS = [
    "schemeVersion",
    "conference",
    "sessions",
    "contents",
    "people",
    "rooms",
]

# Fields whose IDs are referenced by other collections and so must resolve.
REFERENCE_CHECKS = [
    # (collection, id_field, referencing_collection, referencing_field, is_list)
    ("rooms", "id", "sessions", "roomId", False),
    ("people", "id", "sessions", "chairIds", True),
    ("contents", "id", "sessions", "contentIds", True),
    ("tracks", "id", "contents", "trackId", False),
]


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate(data: dict, previous: dict | None, allow_shrink: bool) -> list[str]:
    errors = []

    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in data:
            errors.append(f"missing required top-level key: {key}")

    if errors:
        return errors  # can't safely check further without these

    # No duplicate / missing IDs within each collection
    for collection in ("rooms", "tracks", "sessions", "contents", "people"):
        items = data.get(collection, [])
        ids = [item.get("id") for item in items]
        if any(i is None for i in ids):
            errors.append(f"{collection}: one or more records missing an id")
        dupes = {i for i in ids if ids.count(i) > 1 and i is not None}
        if dupes:
            errors.append(f"{collection}: duplicate ids {sorted(dupes)}")

    # Referential integrity
    id_sets = {
        coll: {item["id"] for item in data.get(coll, []) if "id" in item}
        for coll in ("rooms", "tracks", "sessions", "contents", "people")
    }
    for target_coll, _id_field, source_coll, source_field, is_list in REFERENCE_CHECKS:
        valid_ids = id_sets.get(target_coll, set())
        for item in data.get(source_coll, []):
            value = item.get(source_field)
            if value is None:
                continue
            refs = value if is_list else [value]
            for ref in refs:
                if ref not in valid_ids:
                    errors.append(
                        f"{source_coll}[{item.get('id')}].{source_field} "
                        f"references missing {target_coll} id {ref}"
                    )

    # Record counts within a sane band of the previous revision
    if previous and not allow_shrink:
        for collection in ("sessions", "contents", "people", "rooms"):
            old_count = len(previous.get(collection, []))
            new_count = len(data.get(collection, []))
            if old_count > 0:
                drop = (old_count - new_count) / old_count
                if drop > 0.05:
                    errors.append(
                        f"{collection}: count dropped by {drop:.0%} "
                        f"({old_count} -> {new_count}); use --force to override"
                    )

    return errors


def run_git(args: list[str], cwd: Path) -> None:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(
            f"error: `git {' '.join(args)}` failed:\n{result.stdout}{result.stderr}"
        )
    if result.stdout.strip():
        print(result.stdout.strip())


def next_revision_number(edition_dir: Path) -> int:
    revisions_dir = edition_dir / "revisions"
    existing = sorted(revisions_dir.glob("*.json"))
    if not existing:
        return 1
    return max(int(p.stem) for p in existing) + 1


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("edition", help="e.g. chi2027, sandbox, chi2026")
    parser.add_argument("source", type=Path, help="path to the new programme JSON file")
    parser.add_argument("-m", "--message", default="", help="short note on what changed, stored in version.json")
    parser.add_argument("--force", action="store_true", help="skip the record-count sanity band check")
    parser.add_argument(
        "--push", action="store_true",
        help="commit the published files and push to the current branch's upstream remote",
    )
    args = parser.parse_args()

    if not args.source.exists():
        sys.exit(f"error: source file not found: {args.source}")

    edition_dir = DATA_ROOT / args.edition
    revisions_dir = edition_dir / "revisions"
    revisions_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading {args.source} ...")
    data = load_json(args.source)

    latest_path = edition_dir / "latest.json"
    previous = load_json(latest_path) if latest_path.exists() else None

    print("Validating ...")
    errors = validate(data, previous, allow_shrink=args.force)
    if errors:
        print("VALIDATION FAILED — nothing was published:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    print("OK")

    revision = next_revision_number(edition_dir)
    generated_at = datetime.now(timezone.utc).astimezone().isoformat()

    revision_filename = f"{revision:03d}.json"
    revision_path = revisions_dir / revision_filename

    with revision_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    with latest_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    version_payload = {
        "edition": args.edition,
        "revision": revision,
        "generated_at": generated_at,
        "latest_url": f"https://chidigitalexperience.org/data/{args.edition}/latest.json",
        "revision_url": f"https://chidigitalexperience.org/data/{args.edition}/revisions/{revision_filename}",
    }
    if args.message:
        version_payload["message"] = args.message

    version_path = edition_dir / "version.json"
    with version_path.open("w", encoding="utf-8") as f:
        json.dump(version_payload, f, ensure_ascii=False, indent=2)
        f.write("\n")

    repo_root = DATA_ROOT.parent
    rel_edition_dir = f"data/{args.edition}"

    print(f"Published {args.edition} revision {revision}:")
    print(f"  {revision_path.relative_to(repo_root)}")
    print(f"  {latest_path.relative_to(repo_root)}")
    print(f"  {version_path.relative_to(repo_root)}")
    print()

    commit_message = args.message or f"Publish {args.edition} revision {revision}"
    commit_message += "\n\nCo-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"

    if not args.push:
        print("Nothing has been committed or pushed. Review with `git diff`, then:")
        print(f"  git add {rel_edition_dir}")
        print(f'  git commit -m "{args.message or f"Publish {args.edition} revision {revision}"}"')
        print("  git push")
        return

    print(f"Committing and pushing (--push) ...")
    run_git(["add", rel_edition_dir], cwd=repo_root)

    staged = subprocess.run(
        ["git", "diff", "--cached", "--quiet"], cwd=repo_root
    ).returncode
    if staged == 0:
        print("Nothing changed relative to the last commit; skipping commit and push.")
        return

    run_git(["commit", "-m", commit_message], cwd=repo_root)
    run_git(["push"], cwd=repo_root)
    print("Pushed.")


if __name__ == "__main__":
    main()
