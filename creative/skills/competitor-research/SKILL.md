---
name: competitor-research
description: >
  Run deep competitor and market research for a new brand or campaign. Use this skill
  whenever the user mentions competitor research, market research, customer research, pain
  point discovery, competitive landscape, switching objections, or asks you to "become an
  expert" on a brand's market before writing copy. Also trigger when the user says
  "research this client," "deep dive into the market," "what are customers complaining
  about," "find pain points," or provides a brand URL and asks you to learn the space.
  Even if the user just says "let's start research for [client name]" — use this skill.
  This is the FIRST step before writing any copy for a new brand or campaign angle.
version: 1.0.0
---

# Competitor & Market Research

## Overview

Run comprehensive competitor and market research that produces a structured brief ready to feed into ad copy, landing pages, and campaign strategy. This skill turns a brand URL + target audience + named competitors into an actionable messaging foundation.

This is always the FIRST step before writing any copy for a new brand or new campaign angle. Never skip it. The research brief is what makes the copy specific, credible, and emotionally resonant instead of generic.

The brief is channel-agnostic — the same research feeds Meta Ads, Google Ads, landing pages, and the DR copywriting skill.

## Tools

This skill is research-heavy. Use `WebSearch` and `WebFetch` aggressively — expect 10–20+ tool calls per session. If a richer raw-source backend is available (see **Optional: Agent-Reach** below), prefer it for social and forum pulls because it returns raw posts and comments instead of search snippets. Everything works without it.

## Intake — What You Need Before Starting

When the user triggers this skill, gather these inputs. If critical ones are missing, ask — but don't over-interview. Get moving fast.

**Required:**
- **Target audience** — Who are we trying to reach? Job titles, roles, demographics, psychographics, awareness level.
- **Named competitors** — The user will usually name 2–5 direct competitors. If they don't, ask.

**Primary client source (one or both):**
- **Messaging document** — A doc the user has already built with the brand containing positioning, differentiators, value props, proof points, target audience details, and campaign goals. This is the single best source of client truth. It lives in the conversation (pasted or uploaded), in the project's notes, or as an attached file. ALWAYS check for this first — it outranks the website.
- **Client URL** — The brand's website. Useful for understanding product features, pricing, and social proof, but often has generic or underdeveloped copy that doesn't reflect the real messaging strategy. Treat the website as supplementary to the messaging doc, not the other way around.

**If both exist:** The messaging doc is your primary source for the brand's positioning, differentiators, and audience understanding. The website fills in gaps — pricing specifics, feature lists, testimonial details, case studies — that the messaging doc may not cover.

**If only the website exists:** Scrape it thoroughly but flag in your brief that the brand positioning section is based on website copy alone and may need refinement once the user provides deeper context.

**Helpful but not required (ask if not provided):**
- **Geography** — Where does the brand operate? Country, region, or global.
- **Industry vertical** — What space are they in? (SaaS, local services, ecommerce, etc.)
- **Known differentiators** — What does the user already know makes this client different?
- **Campaign goal** — What's the eventual use for this research? (Meta ads, Google Ads, landing page, full funnel, etc.)

If the user gives you everything upfront, skip the questions and start researching immediately.

## Pre-Research Gate (MANDATORY)

**Before running ANY research, you MUST confirm the messaging document situation.** This is a hard gate — do not proceed to Phase 1 until it is resolved.

If the user has not provided or referenced a messaging document in their prompt, ask explicitly:

> "Do you have a messaging document, client brief, or strategy notes for this client? This is the most valuable source for positioning and differentiators — the website alone often doesn't reflect the real strategy. If you have one, paste it, upload it, or point me to it. If not, I'll work from the website but flag where the brief may need refinement."

**Only proceed once the user either:**
1. Provides the messaging doc (use it as primary source), OR
2. Confirms no messaging doc exists (proceed with website, flag the gap in output), OR
3. Says to skip it and proceed anyway (proceed, but still flag the gap in output)

Do not treat silence or the absence of a messaging doc in the prompt as confirmation it doesn't exist. Ask.

## Research Process

Execute these phases in order.

### Phase 1: Learn the Client

**Start with the messaging document if one exists.** This is the most reliable source of what the brand actually sells, who they serve, what makes them different, and how they want to be positioned. Extract:
- Core product/service and pricing model
- Target audience (their language for who they serve)
- Key differentiators and unique mechanisms
- Proof points (testimonials, stats, case studies, credentials)
- Known pain points they solve
- Brand voice and tone preferences
- Any competitive positioning they've already established

**Then supplement with the brand's website.** The website fills in what the messaging doc doesn't cover — or validates what it claims. Scrape for:
- Feature details and product specifics the messaging doc may gloss over
- Pricing page specifics (exact numbers, tiers, comparison tables)
- Testimonials and case studies not in the messaging doc
- How they describe themselves publicly vs. how the messaging doc positions them (gaps here are useful intel)

**If no messaging doc exists**, scrape the website thoroughly but note that your client positioning section is built on public-facing copy only. Flag this so the user knows to validate.

**Search queries to run either way:**
- `[client name] reviews`
- `[client name] testimonials`
- `[client name] pricing`
- Fetch their homepage, features page, pricing page, and any case study or comparison pages

### Phase 2: Map the Competitive Landscape

For each named competitor, research:
- Their product positioning and pricing
- Their strengths (what customers actually like)
- Their weaknesses and vulnerabilities (what customers hate)
- Their review scores across platforms

**Search queries to run for EACH competitor:**
- `[competitor] reviews complaints`
- `[competitor] BBB reviews`
- `[competitor] Capterra reviews`
- `[competitor] G2 reviews`
- `[competitor] Reddit complaints`
- `[competitor] pricing expensive`
- `[competitor] vs [other competitor]`
- Fetch their homepage and pricing page

**What you're looking for:**
- Patterns in negative reviews (these become campaign pain points)
- Pricing structures that create resentment (hidden fees, per-user charges, aggressive upselling)
- Customer service failures (response times, quality of support, BBB ratings)
- Feature gaps that the brand fills
- Lock-in tactics or switching barriers competitors use

**Log every instance as you go** — see the Evidence Log below. You cannot rank by frequency in Phase 4 if you didn't record instances here.

### Phase 3: Understand the Customer

Research what real customers in this market are saying — not what companies say about themselves.

**Search queries to run:**
- `[industry] software frustrations Reddit`
- `[industry] switching [product type] fear`
- `[target audience role] complaints [product type]`
- `[industry] forum [product type] problems`
- `"switching from [competitor]" [industry]`

**What you're looking for:**
- The language real people use to describe their pain (use their words, not marketing words)
- Emotional triggers — what makes them angry, anxious, or frustrated
- The moment they start considering a switch (what breaks the camel's back)
- What they wish existed but can't find
- Objections to switching (fear of migration, training, downtime, data loss)

#### Tool: Reddit Answers (discovery layer, not a quote source)

Reddit Answers (`reddit.com/answers`) is Reddit's AI search. It scans posts AND comments across every subreddit and returns a summarized response with links back to the original threads. Use it to find the right conversations fast — it's a much faster way to surface relevant threads than guessing subreddits and keyword-searching by hand.

**Use the persona + pain prompt formula:**

> [Task] + [target audience persona] + [pain/emotional framing]

The task is almost always "Find posts and comments from…" and the pain framing pushes it toward raw, emotional, lived-experience threads rather than how-to content. Examples:

- `Find posts and comments from youth sports club admins sharing real challenges, frustrations, and relatable situations with their registration software`
- `Find posts and comments from salon owners venting about backbar inventory and product waste`
- `Find posts and comments from people over 50 describing dental anxiety and what made them avoid the dentist`
- `Find posts and comments from [competitor] users who regret switching or want to leave`

You can ask follow-up questions in the same thread to drill into a specific pain once a theme emerges.

**CRITICAL — the summary is the map, not the treasure.** Reddit Answers hands you a polished AI summary. That summary is exactly the kind of cleaned-up paraphrase this skill exists to avoid (see Quality Standards below). **Never paste the Reddit Answers summary into the brief.** Use it only to locate threads, then click through to the linked posts and comments and pull the rawest verbatim language straight from the source. The quote that goes in the brief comes from a real comment you opened — not from the AI's summary of it.

**Practical notes:**
- Be logged in. Logged-in users get ~20 questions/day; logged-out visitors are capped at ~10/week.
- Available in Canada (and the US, UK, Australia, India, and others), so it's usable from Canada.
- Secondary use: it also works for competitor sentiment in Phase 2 (e.g. "Find posts and comments from people complaining about [competitor]") — same rule applies, mine the linked threads for verbatim language, don't lift the summary.

Treat Reddit Answers as one tool in the kit alongside manual `WebSearch` of Reddit, BBB, Capterra, G2, and forums — not a replacement for them. Different tools surface different threads.

#### Optional: Agent-Reach (raw-source accelerator)

[Agent-Reach](https://github.com/Panniantong/Agent-Reach) is an optional CLI that gives free, no-API access to raw posts and comments on Reddit, Twitter/X, YouTube (transcripts), and RSS feeds. It is **not required** — this skill works fully with `WebSearch` / `WebFetch` + Reddit Answers. Use it only when it's already installed and healthy, because it returns raw lived-experience text (the exact verbatim quotes this skill is built on) instead of search snippets.

**Decision rule — fail gracefully:**
1. Check availability once: run `agent-reach doctor`.
2. If it reports a working backend for a platform, use it for that platform's raw pulls in Phases 2–3 (e.g. Reddit comment threads, X complaint searches, YouTube review-video transcripts, "X vs Y" comparison videos).
3. If the command is missing, errors, or reports the backend as broken, **silently fall back** to `WebSearch` / `WebFetch` + Reddit Answers. Do not ask the user to install it mid-session and do not block research on it.

**Where it adds the most:**
- Phase 3 customer voice — direct Reddit comment scraping and X searches for raw pain language.
- Phase 2 competitor recon — YouTube transcripts of review and comparison videos, Reddit complaint threads.

**Guardrails:**
- Read-only research use only. Do not use it for LinkedIn scraping — low signal for pain points and high account risk.
- Same sourcing rule as everywhere else: a quote in the brief must come from a specific real post/comment you actually pulled, never from a tool's summary.

### Phase 4: Synthesize Into the Brief

Once research is complete, organize everything into the output structure below.

**Critical methodology for ranking — keep an Evidence Log.** As you research Phases 2 and 3, maintain a running tally so the ranking is auditable rather than a vibe. For each distinct complaint, desire, or objection theme, record one row:

| Theme | Type (pain / desire / objection) | Source | Verbatim snippet | Competitor (if any) |
|-------|----------------------------------|--------|------------------|---------------------|

When you encounter "support is slow" in 4 separate BBB reviews, 2 Capterra reviews, and 3 Reddit threads, that's 9 rows for one theme. When "too expensive" appears in 3 BBB reviews and 1 Capterra review, that's 4 rows. **Rank by row count first.** Use emotional severity as a tiebreaker when two themes have similar counts — the one that provokes stronger language (anger, desperation, betrayal) ranks higher. The log is your working artifact; you don't paste the whole table into the brief, but the frequency numbers you cite must trace back to it.

**Critical methodology for descriptions:** Lead with the rawest, most emotionally charged verbatim quotes you found. These are copy ammunition — the exact words real customers use. Do NOT paraphrase customer language into polished summaries. A cleaned-up summary like "customers feel pricing is opaque" is useless for writing ads. The raw quote "We started getting charged MORE for not using online registration" is what a copywriter needs. Pull the best 2–3 verbatim quotes per pain point, then add your context and analysis around them.

The brief should feel like a strategic document built on hard evidence, not an editorial opinion piece.

## Output Structure

Deliver the research as a structured brief using this exact format. Every section is required.

After delivering the brief in chat, **offer to save it as a file** so downstream skills (Meta/Google ad work, the `direct-response-copywriter` skill) can load it:

> "Want me to save this brief to a file so the copywriting and ad skills can pull from it? I'll write it to `research/[client-name]-research-brief.md`."

Save only if the user agrees (or if a project convention already calls for it). Use the brand name and a clear `*-research-brief.md` filename.

---

### SECTION 1: MARKET LANDSCAPE
A 2–3 paragraph overview of the competitive space. Who are the major players? What's the market dynamic? Any macro trends (consolidation, pricing pressure, regulatory changes) that create opportunity?

### SECTION 2: CLIENT POSITIONING
Summary of the brand's positioning, key differentiators, and messaging strengths — drawn primarily from the messaging document if provided, supplemented by website copy. Note any gaps between how the messaging doc positions the brand and what the website actually communicates (these gaps are opportunities).

**MANDATORY:** If no messaging document was provided or reviewed, begin this section with the following disclaimer before any content:

> ⚠️ **Source note:** This section is based on public website copy only. No messaging document was reviewed. Treat positioning insights as preliminary — validate against internal client strategy before using in final copy.

Do not skip this disclaimer. It exists to prevent downstream copy from being built on an incomplete foundation.

### SECTION 3: CUSTOMER PAIN POINTS (Ranked by Frequency)
List the top 5–7 pain points, **ranked by row count in your Evidence Log** — how many distinct instances of each theme appeared across your research sources. This is a data-driven ranking, not an editorial judgment.

For each pain point:
- **Name it** in plain language (this becomes a potential campaign angle)
- **Frequency indicator** — Note approximately how many distinct instances of this complaint you encountered and across which sources (e.g., "Appeared in 9 separate reviews across BBB, Capterra, and Reddit")
- **Verbatim customer quotes** — Pull the 2–3 rawest, most emotionally charged quotes you found for this theme. These are the foundation. Present them as direct quotes before adding any analysis.
- **Your analysis** — After the quotes, add context: what pattern they reveal, how severe the emotional charge is, and which competitors are most associated with this pain
- **Note which competitors it's most associated with**

Format each pain point as a short section with a bold name, not a bullet list. Lead with the customer's voice, not yours.

### SECTION 4: COMPETITOR VULNERABILITIES
For each competitor researched, provide:
- **Overall rating/reputation** (BBB score, Capterra/G2 rating, general sentiment)
- **Top 2–3 specific vulnerabilities** the brand can exploit in messaging
- **Pricing comparison** vs. the brand (specific numbers where available)
- **Customer service assessment** (response time, quality, common complaints)

**After the individual competitor breakdowns, include a consolidated pricing comparison table.** This table should show, side by side: the brand's pricing vs. each competitor's pricing. Include platform/subscription fees, per-transaction or per-registrant fees, and any other recurring costs. Use actual dollar amounts — not ranges or vague descriptors. If a competitor doesn't publish pricing, note that explicitly ("pricing not publicly listed — sales call required"). This table is one of the most referenced assets in downstream copy work.

### SECTION 5: SWITCHING OBJECTIONS
List the top 3–5 reasons prospects resist switching platforms/providers, even when unhappy. **Only include objections that appeared in actual customer language during research** — do not invent plausible-sounding objections. If customers aren't talking about it, it doesn't belong here.

For each:
- **Name the objection**
- **Verbatim evidence** — Quote or closely paraphrase the actual customer language where this objection surfaced
- **Explain why it feels real to the prospect**
- **Provide the counter-argument** the brand can use to overcome it
- **Tie the counter-argument to a specific client proof point** — a testimonial, case study, stat, or feature that directly neutralizes the objection. Generic reassurance ("it's easy to switch") is not enough. The counter needs evidence.

### SECTION 6: DESIRED BENEFITS (Ranked by Frequency)
What does the target audience actually want? List the top 5–7 benefits they're seeking, **ranked by row count in your Evidence Log** — not by what you think is most important.

For each benefit:
- **Name it as an outcome**, not a feature (e.g., "Hours back from admin work" not "AI scheduling tool")
- **Frequency indicator** — How often did this desire appear and where?
- **Verbatim customer language** — Pull 1–2 quotes that express this desire in the customer's own words
- **Which client feature or differentiator maps to this benefit** — Connect the customer desire to a specific thing the brand offers

### SECTION 7: CAMPAIGN ANGLES & BIG IDEA

This is where research turns into strategy. Based on everything above, recommend:

**The Big Idea:** One overarching campaign concept that ties the strongest pain point to the brand's strongest differentiator. This should be a single sentence or phrase that could anchor an entire campaign.

**3–5 Campaign Angles:** Each angle is a distinct messaging strategy that could become its own ad set or campaign theme. For each angle:
- **Angle name** (short, descriptive)
- **The pain point it targets** (reference Section 3)
- **The client differentiator it leverages**
- **A sample headline or hook** that captures the angle
- **Why it works** (1–2 sentences connecting the research to the strategy)

**Recommended Campaign Structure:** Suggest how these angles could be phased or sequenced (e.g., Phase 1: Problem-aware ads targeting pain point X, Phase 2: Solution-aware ads featuring differentiator Y, Phase 3: Decision-stage ads addressing switching objection Z).

---

## Quality Standards

Before delivering the brief, verify:

- [ ] **Ranked by frequency, not opinion.** Pain points and benefits are ordered by Evidence Log row count, not editorial judgment. If you can't point to multiple instances across sources, it shouldn't be ranked high.
- [ ] **Verbatim quotes lead every pain point.** Each pain point section starts with 2–3 raw customer quotes before any analysis. If the quotes aren't there, the section isn't done.
- [ ] **No paraphrasing customer language into polished summaries.** "Customers feel pricing is opaque" is a failure. "We started getting charged MORE for not using online registration" is what we need.
- [ ] **No AI-summary quotes.** Every quote traces to a specific post or comment that was actually opened and read. Nothing in the brief is lifted from a Reddit Answers summary, an Agent-Reach summary, or any other AI summary — those are for finding threads, not for sourcing quotes.
- [ ] **Specificity over generality.** Every claim is backed by a specific data point, quote, rating, or example.
- [ ] **Actionable angles.** The campaign angles section gives the user enough to start writing copy immediately — not just "target their pricing" but a specific hook and the reasoning behind it.
- [ ] **Competitor numbers.** Pricing comparisons use actual dollar amounts where available, not vague descriptors like "expensive."
- [ ] **Switching objections are evidence-based.** Every objection must trace to actual customer language. If customers aren't saying it, don't include it.
- [ ] **The big idea connects pain to differentiator.** It's not just clever — it's strategically grounded in the research.
- [ ] **Pricing comparison table is present and complete.** Side-by-side with real dollar amounts for every competitor.

## What This Skill Does NOT Do

- It does not write final ad copy, landing pages, or video scripts. That's the `direct-response-copywriter` skill's job.
- It does not create client-facing documents. The output is a working brief for internal use.
- It does not replace the user's judgment. Present the research and recommendations, then let the user decide which angles to pursue.

## Triggering Notes

This skill should fire BEFORE the `direct-response-copywriter` skill when working with a new brand or new campaign angle. The research brief this skill produces is the input that makes the copywriting skill's output specific and effective.

If the user asks to "write ads for [new brand]" and no research has been done yet, suggest running this skill first. The user may decline — that's fine, proceed with what you have. But always offer.
