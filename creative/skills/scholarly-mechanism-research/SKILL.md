---
name: scholarly-mechanism-research
description: "Run deep, source-verified scientific research on a brand's problem and mechanism so ad creative can be backed by real peer-reviewed evidence. Use this skill whenever the user wants to ground a campaign in research — phrases like 'research the problem for [brand],' 'find studies on [condition/pain],' 'what does the research say about [X],' 'build a medical-paper / research-screenshot creative,' 'find a stat we can use,' 'find scientific proof for this angle,' or any request that needs prevalence, mechanism, or origin evidence for an offer that solves a researchable condition or pain. Also trigger when reverse-engineering why a problem exists, when an ad needs an authoritative third-party citation, or when the user references Google Scholar, PubMed, a journal, or a study. This is the scientific-proof layer that pairs with competitor-research (market/customer voice) and ad-creative-strategist (formats). Even if the user just says 'let's find some research for [brand]' — use this skill."
version: 1.0.0
---

# Scholarly Mechanism & Problem Research

## Overview

Turn a brand's problem into a set of verified, citable scientific findings that make ad creative credible instead of asserted. This skill finds the real research behind a condition or pain — how common it is, what actually causes it, and where it comes from — verifies every claim at the primary source, and hands back creative-ready ammunition: a research brief plus screenshot/angle specs.

This is the **scientific-proof layer**. It sits alongside two other skills and does not replace them:
- `competitor-research` owns market dynamics, competitor messaging, and customer voice.
- `ad-creative-strategist` owns creative formats and concepts.
- **This skill** owns peer-reviewed proof — the third-party authority that lets a creative say "this is documented" rather than "trust us."

Use it when the offer solves something a body of research exists on: health and medical (dental anxiety, chronic pain, sleep), behavioral and psychological (procrastination, financial stress), material/scientific (how a product mechanism works), or any pain where a study can lend authority.

## Intake — What You Need Before Starting

Gather these. If critical ones are missing, ask — but don't over-interview. Get moving.

**Required:**
- **The problem or condition** — What pain, fear, condition, or mechanism are we researching? (e.g., "dental anxiety in adults 50+")
- **Audience** — Who feels it? Demographics and geography matter, because prevalence stats are population-specific (a US stat for a US audience).

**Helpful but not required (ask if unclear):**
- **The angle being considered** — Are we proving the problem is common (prevalence), reframing its cause (mechanism), or relocating blame (origin)? This focuses the search.
- **Intended creative format** — Medical-paper screenshot, body-copy proof point, advertorial, video hook. Affects what gets extracted and how it's specced.
- **Client claims to pressure-test** — Any stat or mechanism claim the brand or a prior draft already used that needs independent verification.

If the user gives everything upfront, skip the questions and research immediately.

## Source Hierarchy & Tools

Google Scholar has **no official API**, and every Scholar-scraping tool gets rate-limited or CAPTCHA-blocked without a proxy. So do not lean on Scholar as the backbone. Work top-down:

1. **API-backed academic sources first** (reliable, structured, license-aware):
   - **PubMed / Europe PMC** — biomedical and health. Best for medical clients.
   - **Semantic Scholar** — 200M+ papers across all fields, citation graph.
   - **OpenAlex** — fully open, broad coverage, no key.
   - If an MCP for any of these is connected, use it. Otherwise use `web_search` + `web_fetch` against these sources directly.
2. **`web_search` + `web_fetch`** — the default when no MCP is wired up. This is enough for most creative research (it's how the DDC dental-anxiety set was built). Search the journal name, DOI, or study title; fetch the journal page or the PubMed/Europe PMC record.
3. **Google Scholar scrapers** — supplement only, never the backbone. Expect failures.

When a primary source blocks the fetch (e.g., a CAPTCHA), find the same finding via the journal site, Europe PMC, the abstract on the publisher page, or a secondary source that quotes the exact figure — then trace it back to the original before using it.

## Research Process

Execute in order. Expect 8–15+ tool calls. Use search aggressively.

### Phase 1: Frame the Three Targets

Every problem gets researched along three axes. Decide which the creative needs (often all three):

- **Prevalence** — How common is it? ("X% of [population] experience [condition].") Powers normalization and "you're not alone" angles — but see the angle caution in the hard rules.
- **Mechanism** — What actually drives it? ("It's not the pain, it's the loss of control.") Powers reframe angles and unique-mechanism positioning. Usually the highest-value axis for direct response, because it sets up the brand's solution.
- **Origin** — Where does it come from? ("It traces back to a past experience, not the person.") Powers absolution / blame-shift angles.

Write the specific search targets before searching (e.g., "US prevalence of dental anxiety," "what patients fear most in the chair," "documented origins of dental phobia").

### Phase 2: Retrieve

Search each target separately — never bundle multiple findings into one query. For each promising result, capture: exact title, journal, year, authors, the specific finding, the population/sample, and whether it's US or global.

### Phase 3: Verify at the Primary Source (non-negotiable)

For every stat or claim that might enter a creative, open the actual paper (or its abstract/record) and confirm:
- The **number** is reported as stated (not rounded, not drifted through retellings).
- The **population and sample** match how we'd use it (a severe-phobia subsample is not "all adults"; a 30-person qualitative study is not population-representative).
- The **geography** (US vs global) matches the audience.
- The finding actually **says what the angle needs** — not something adjacent.

Never accept a figure because it's repeated across marketing blogs. Trace it to the source or drop it.

### Phase 4: Triage Into Three Buckets

Sort every finding:
- **Ship-ready** — verified, correctly represented, audience-appropriate. Cite and use.
- **Needs a qualifier** — true but narrow (small sample, severe subgroup, global not US). Usable *with* an honest qualifier baked into the phrasing.
- **Cut — marketing fluff** — round numbers with no traceable primary source (the "30 million Americans" type). Flag and discard; propose a verified alternative.

## Verification Rules (baked in — this is the point of the skill)

These enforce the standard that anything entering a creative is something the user shouldn't have to fact-check.

- **Real titles and real findings only.** Never invent a study, a journal, a stat, or an author. Never put words in a real paper's mouth. If you're unsure a paper says it, don't use it.
- **The paper proves the PROBLEM, never endorses the SOLUTION.** Research establishes that the condition is real, common, or caused a certain way. It never implies the journal endorses the brand or their mechanism. Keep a clean wall: evidence inside the citation, client claims outside it.
- **Re-verify when a claim changes format.** A stat moving from body copy into a screenshot, diagram, or headline makes a stronger implied claim than it did as prose — re-check it against the source at the new strength.
- **US vs global, always labeled.** For a US audience, lead with US data. Flag any global or non-representative figure explicitly.
- **Copyright discipline.** Paraphrase. Any verbatim quote stays short and gets attributed. Never reproduce large blocks of a paper. Prefer open-access papers when a creative needs to show real article text.
- **No efficacy or medical-outcome promises.** Research can describe a problem; it cannot license "cure," "guaranteed," or outcome claims for the brand. Watch for this when findings tempt a strong promise.
- **Client-attributed ≠ verified.** If a number comes only from the brand (proprietary case counts, internal data) and no independent source exists, label it client-attributed and confirm the brand stands behind it. Don't dress it up as independently verified.

## Output 1 — The Research Brief

Deliver in chat (or a doc if asked). Use this structure:

```
# [Client] — [Problem] Research Brief

## Verification status (read first)
- What's ship-ready, what needs a qualifier, what was cut and why.
- Any client-attributed claims that still need confirmation.

## Prevalence findings
- [Finding] — [exact figure] — [Journal, Year] — [population/geo] — [status]

## Mechanism findings
- [Finding] — [exact figure/result] — [Journal, Year] — [population/geo] — [status]

## Origin findings
- [Finding] — [exact figure/result] — [Journal, Year] — [population/geo] — [status]

## Cut list (do not use)
- [Claim] — [why it failed verification] — [verified alternative if any]
```

Every line is backed by a specific source. No unsourced assertions.

## Output 2 — Creative Specs

For each ship-ready finding the creative will use, provide:

**Medical-paper / research-screenshot spec** (when that format is in play):
- **Journal/title (verbatim):** the real title, journal, year.
- **Subheading shown:** Results / Background / etc.
- **Blurb:** a faithful paraphrase styled as paper text (paraphrase over verbatim unless open-access).
- **Highlighted call-out line:** the verified finding, phrased compliantly (third person; no "you have [condition]").
- **Production note:** the screenshot must read as an organic article capture, not a designed ad — and nothing about the brand goes inside the screenshot.

**Angle mapping:** for each finding, name the copy angle it sets up (normalization / reframe / absolution) and the one-line hook direction — then hand off to `ad-creative-strategist` and `direct-response-copywriter`. This skill stops at specced ammunition; it does not write final copy.

## Hard Rules Recap

1. Real titles and findings only — never fabricate, never misattribute.
2. Paper proves the problem; client claims live outside the citation.
3. Verify at the primary source; re-verify on format change.
4. Label US vs global and sample limitations.
5. Short attributed quotes; paraphrase by default; respect copyright.
6. No efficacy/outcome promises licensed off research.
7. Client-attributed is not independently verified — label it.

## Worked Example — DDC (dental anxiety, adults 50+)

The flow this skill encodes, from a real build:

- **Framed three targets:** prevalence (how common is dental anxiety), mechanism (what patients actually fear), origin (where it starts).
- **Retrieved + verified at source:**
  - Prevalence — JADA 2025 census-matched US survey: 72.6% afraid (45.8% moderate, 26.8% severe). *Ship-ready, US.*
  - Mechanism — BMC Psychiatry 2004 (Moore et al.): among severe-phobia patients, 47% cited powerlessness vs 30% pain. *Needs qualifier (severe subsample) — which actually sharpened the angle.*
  - Origin — Frontiers in Oral Health 2025: main origins were a traumatic dental visit in childhood or adulthood. *Ship-ready.*
- **Cut list:** "30 million Americans" type round numbers — no traceable primary source. Replaced with the JADA figure.
- **Creative specs:** Frontiers paper → V1 screenshot (origin/absolution); Moore paper → V2 screenshot (mechanism/"it was never the drill"). Both specced as organic article captures with verbatim titles and compliant call-out lines; all client copy kept below the screenshot.
- **Result:** two medical-paper creatives where every on-image number was independently verified, and the angle that won (mechanism/absolution) was the one the research supported best.
