# Notion source — example config

The format taxonomy in `SKILL.md` is self-contained and works with no setup. This file wires up an **optional live enrichment** on top of it: if you keep the format library in Notion, the skill can read the per-format page before writing a brief and pick up content the repo doesn't carry.

What the Notion pages add over `SKILL.md`:

- **A JSON prompt template per format** — the full key structure filled in for that specific format, with bracketed placeholders. This is the layer that gets a usable image on the first generation instead of the third.
- **Reference examples** — attached screenshots of real ads in that format.
- **Anything added since the repo was last updated** — new formats and edits land in Notion first.

## Setup

1. Copy this file to `notion-source.md` in the same directory. That filename is gitignored, so your workspace URL and IDs never enter the repo.
2. Fill in the two values below from your own Notion.
3. Make sure the Notion MCP connector is enabled in your Claude Code session.

To find the data source ID: open your format library database in Notion, then have Claude `notion-fetch` the database URL. The result contains a `<data-source url="collection://…">` tag — that UUID is what you want.

## Config

```
page_url:        https://www.notion.so/<your-workspace>/<your-format-library-page>
data_source_id:  collection://00000000-0000-0000-0000-000000000000
```

## Field reference

| Field | What it's for |
|---|---|
| `page_url` | The parent page. Useful for a human to open; not required for querying. |
| `data_source_id` | The queryable collection. Required — this is what `notion-query-data-sources` takes. |

## How the skill uses it

When this file exists and the Notion connector is available:

1. Query the data source for the current row set — `Name`, `Section`, `Aspect Ratio`, `Template Type`, and `url`. That's the authoritative list of which formats exist right now.
2. Reconcile against `SKILL.md`. Rows not in the repo's table are new formats — use them, reasoning from the name and section, and mention to the user that they aren't documented locally yet.
3. Before writing a brief or generating a JSON prompt for a specific format, fetch **that format's page** and use its JSON prompt template rather than reconstructing one.

When this file is absent, or the connector isn't available, the skill runs on `SKILL.md` plus `format-detail.md` alone and says nothing about it. The local files are complete enough to work from — this is enrichment, not a dependency.

## Expected drift

Notion is the live source, so it leads. The repo's 53-format table is a snapshot that gets updated deliberately. When the two disagree on *which formats exist*, Notion wins. When they disagree on *how a format works*, the repo's `format-detail.md` is the considered write-up and Notion's page may be thinner — the older formats (1–42) carry only a JSON prompt, with no prose spec at all.
