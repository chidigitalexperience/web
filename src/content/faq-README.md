# FAQ content

Each Markdown file in `src/content/faq/` is one FAQ entry, rendered on the
`/faq` page. This file itself lives one level up so it isn't picked up as an
entry.

To add a question: create a new `.md` file here with this frontmatter:

```md
---
question: "Your question text"
order: 3
---

Your answer, in Markdown.
```

`order` controls display order (lowest first). Set `placeholder: true` on
entries that are not real content yet (see `placeholder-1.md` and
`placeholder-2.md`) — the site marks these visually and they should be
replaced or deleted before launch.

No code changes or rebuild step beyond the normal deploy are needed to add,
edit, or remove an entry.
