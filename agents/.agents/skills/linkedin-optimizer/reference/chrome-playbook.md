# Chrome playbook (Claude-in-Chrome)

How to edit LinkedIn live, safely. LinkedIn's UI changes often: URLs below were valid 2026-10; if one 404s or looks different, navigate via the pencil (✏️) icons on the profile instead.

## Contents
1. Setup
2. Golden loop (every section)
3. Edit URLs
4. Section notes
5. Traps
6. Fallback

## 1. Setup
- Load all browser tools you need in one ToolSearch call; call `tabs_context_mcp` first, create a new tab (don't hijack the user's tabs).
- Confirm the logged-in account is the person being optimized (name on `/in/me/`). If not, stop.
- Get the profile slug from the URL after `/in/me/` redirects.

## 2. Golden loop (every section)
1. Tell the user exactly what you will save ("Saving headline: '…' (182/220 chars)"). Wait for yes (rule 7).
2. Navigate to the edit dialog. **Read the page** (`read_page`/`find`) before typing; identify the exact field.
3. Check the text fits the limit **before** pasting.
4. Clear the field fully (select all → delete), then type/`form_input` the new text. Rich-text fields: verify no leftover text and line breaks preserved.
5. Find any "Notify network" / "Share with network" / "Share profile updates" toggle → **turn OFF** (rule 5).
6. Save. Wait for the dialog to close.
7. **Verify**: reload the profile section and screenshot/read it; compare to approved text. Report ✅ or the diff.
8. One section per save. Never batch multiple sections into one unconfirmed run.

## 3. Edit URLs (replace `<slug>`)
| Section | URL |
|---|---|
| Intro (name, headline, location, current position) | `https://www.linkedin.com/in/<slug>/edit/intro/` |
| About | `https://www.linkedin.com/in/<slug>/edit/about/` (or ✏️ on About card) |
| Experience list | `https://www.linkedin.com/in/<slug>/details/experience/` → ✏️ per role |
| Projects | `https://www.linkedin.com/in/<slug>/details/projects/` |
| Skills | `https://www.linkedin.com/in/<slug>/details/skills/` |
| Languages | `https://www.linkedin.com/in/<slug>/details/languages/` |
| Education | `https://www.linkedin.com/in/<slug>/details/education/` |
| Custom URL | `https://www.linkedin.com/public-profile/settings` |
| Open to Work | profile → "Open to" → "Finding a new job" (or edit existing Open to Work card) |

## 4. Section notes
- **Headline** lives in Intro. Don't change name/location without explicit ask.
- **About**: paste as plain text with blank lines between paragraphs; no markdown (`**` shows literally). Bullets: use "•" or "–".
- **Experience**: edit title, description, skills per role. Don't change dates/employment type unless approved. Old media attachments: leave unless user says remove (that's a deletion → user does it).
- **Skills**: add via "Add skill"; LinkedIn suggests canonical names — pick the canonical one (e.g. "React.js"). Top/pinned skills: up to 5 shown on profile; reorder via the skills section ✏️ if available.
- **Projects**: name, description, dates, associated position (optional), link via "Add media/link".
- **Open to Work**: titles must be picked from LinkedIn's list — if an exact title doesn't exist, pick the closest and tell the user. Visibility default "Recruiters only" (rule 11).
- **Custom URL**: if taken, propose variants (`firstlast`, `first-last`, `firstmlast`). Warn old URL redirects only for a while.
- **Languages**: fix proficiency labels; language names in profile language.

## 5. Traps
- Modals that ask "Share with your network?" after saving a position → choose **No/Don't share**.
- Autocomplete dropdowns (titles, companies, skills): wait for the list, pick the exact option, verify the chip.
- Character counters: if over, shorten with user approval, never truncate silently.
- Popups (Premium upsell, surveys): dismiss, never accept trials.
- Never trigger JS alerts/confirm dialogs; avoid "Delete" buttons entirely (rule 8).
- Session/2FA/captcha prompts → stop and ask the user to handle it.
- Following/unfollowing pages or people: only with explicit per-account yes (rule 6).

## 6. Fallback
If a section fails twice (element not found, save does nothing, UI changed): stop automating that section, give the user the paste-ready text and where to paste it, continue with the next section.
