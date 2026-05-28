---
name: to-prd
description: Turn the current conversation context into a PRD and publish it to the project issue tracker. Use when user wants to create a PRD from the current context.
---

This skill takes the current conversation context and codebase understanding and produces a PRD. Do NOT interview the user — just synthesise what you already know.

See `docs/agents/trackers.md` for where PRDs are published in this repo.

## What a PRD is

A PRD defines **what** a product or feature should do, **why** it should exist, **who** it is for, and **how success will be measured**. It is not a technical implementation document.

Use these 12 questions as a generation guide — they do not become section headers:

1. What problem are we solving?
2. Who are we solving it for?
3. Why does this matter?
4. What should the product or feature do?
5. What is included in scope?
6. What is explicitly out of scope?
7. What are the expected user flows?
8. What edge cases need to be handled?
9. What constraints or dependencies exist?
10. What product decisions have already been made?
11. What open points, unresolved questions, or pending decisions still exist?
12. How will we know the work is successful?

## Tone

- Short sentences, active voice
- **must** for hard requirements, **should** for strong preferences, **may** for optional behaviour
- Use domain vocabulary consistently (actors, entities from the project glossary)
- Written for a mixed audience: engineers, PMs, and stakeholders — avoid jargon, explain decisions in plain language

## Formatting rules

### Requirements section

Use **Toggle Heading 3** (`### heading {toggle="true"}`) for each feature area group. **Children MUST be indented with a tab** — unindented content sits outside the toggle in Notion and will not be collapsible.

✅ Correct — content indented under toggle:

```
### Event management {toggle="true"}
  Operators must be able to create an event with title, description, cover image...
  Operators must be able to cancel an event. All confirmed guests must receive a cancellation email.
```

❌ Wrong — content not indented, sits outside toggle:

```
### Event management {toggle="true"}
Operators must be able to create an event...
```

No user stories inside Requirements. User stories live in the last section only.

### Data Model section

Use **Toggle Heading 3** (`### heading {toggle="true"}`) for each entity. All descriptive content, state machine diagrams, and decision callouts must be tab-indented inside the toggle.

```
### Events {toggle="true"}
  An event stores: title, description (rich text, nullable for stubs), dates, place...
  **Cancellation is soft-delete.** The row stays in the database but disappears from the investor portal.

### Event guests {toggle="true"}
  Each guest row links an event to either a Heritage user or an anonymous attendee...
```

### User Stories section

`## User Stories` is a **plain H2 heading — NO `{toggle="true"}`**. The actor-level `<details>` blocks go directly underneath it.

Structure: **actor → domain → numbered list of stories**. The domain level emerges naturally from the feature — name domains after areas of behaviour (e.g. "event creation", "RSVP", "notifications", "guest management").

**Critical:** domains are NOT actors. Never create a top-level actor for something that is a behaviour within an existing actor (e.g. "RSVP" and "Notifications" are domains under "Invited investor", not separate actors).

**Actors** are the humans and systems that interact with the product: e.g. Operator, Invited investor, System.
**Domains** are areas of behaviour within an actor's scope: e.g. under "Invited investor" → "Event discovery", "Event detail", "RSVP", "Notifications".

```
## User Stories

<details>
<summary>Operator</summary>
  <details>
  <summary>Event creation</summary>
    1. As an operator, I want to create an event...
    2. As an operator, I want to save a stub...
  </details>
  <details>
  <summary>Guest management</summary>
    1. As an operator, I want to add a Heritage user...
  </details>
</details>
<details>
<summary>Invited investor</summary>
  <details>
  <summary>Event discovery</summary>
    1. As an invited investor, I want to see a list of my events...
  </details>
  <details>
  <summary>RSVP</summary>
    1. As an invited investor, I want to express interest...
  </details>
  <details>
  <summary>Notifications</summary>
    1. As an invited investor, I want to receive an email when I'm invited to an event, so that I'm notified even when I'm not logged into the portal.
  </details>
</details>
```

**This list must be extremely extensive and cover all aspects of the feature.** Every meaningful actor interaction — including edge cases, error states, permissions, filtering, and notification flows — must have a corresponding story. Aim for completeness over brevity.

Each story: `As a <actor>, I want <feature>, so that <benefit>.`

## Data model

If the feature involves database changes, include a **Data Model** section (placed after Success Criteria). Write in non-technical language — describe entities, their purpose, relationships, and key product decisions.

Include state machine diagrams. Explain privacy defaults, semantics, and key rules in plain English. No column definitions, no migration code, no SQL. Use Toggle Heading 3 per entity.

## Process

1. Explore the repo to understand the current state, if you haven't already. Use the project's domain vocabulary. Respect any ADRs in the area.

2. Write the PRD using the template below. Focus on product decisions — **what** the system must do and **why**. No architecture patterns, API contracts, or test strategy. Schema is the exception: include it in the Data Model section if it encodes product behaviour.

3. Publish it to the Definition system defined. See @docs/agents/trackers.md

4. **Read and evaluate.** Immediately after publishing, fetch the page back and verify:
   - Every Requirements sub-section is a H3 toggle with all prose content tab-indented inside it (no content sitting outside a toggle)
   - `## User Stories` has no `{toggle="true"}` attribute
   - Every Data Model entity is a H3 toggle with all content tab-indented inside it
   - No domain (e.g. RSVP, Notifications) appears as a top-level actor in User Stories
   - All `<details>`/`<summary>` tags are unescaped and syntactically correct
   - Format matches the template and tone guidelines
     If any issue is found, apply targeted fixes with `update_content` before reporting done.

<prd-template>

> **DRAFT.** Review before implementation — do not build without human sign-off.

## Problem Statement

Describe the problem from the user's perspective. Who is affected, what pain do they experience today, and why does it matter?

## Users & Context

Name the actors. For each: their role, what they do today (if relevant), and what changes for them.

## Requirements

### Feature area {toggle="true"}

Prose requirements using must / should / may. All text tab-indented under the toggle heading.
No user stories here.

### Another feature area {toggle="true"}

Prose requirements...

## Constraints & Dependencies

Bullet list of non-negotiable constraints. Context for implementors — not implementation decisions.

## Open Points

Unresolved questions, pending decisions, or areas needing clarification before implementation. Be explicit — implicit open points become bugs.

## Success Criteria

How will we know this feature succeeded? Measurable outcomes where possible.

## Data Model _(if applicable)_

### Entity name {toggle="true"}

Plain-language description of the entity, its purpose, and key product decisions encoded in the schema.
State machine diagrams where relevant.

### Another entity {toggle="true"}

...

## User Stories

<details>
<summary>Actor name</summary>
  <details>
  <summary>Domain name</summary>
    1. As a <actor>, I want <feature>, so that <benefit>.
    2. ...
  </details>
  <details>
  <summary>Another domain</summary>
    1. ...
  </details>
</details>
<details>
<summary>Another actor</summary>
  <details>
  <summary>Domain name</summary>
    1. ...
  </details>
</details>

</prd-template>
