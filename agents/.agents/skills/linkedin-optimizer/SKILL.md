---
disable-model-invocation: true
name: linkedin-optimizer
description: Audits and rewrites a person's LinkedIn profile for recruiter and AI-sourcing search (headline, About, experience, projects, skills, Open to Work, custom URL), scores it out of 100 before and after, applies changes as paste-ready text or live via Claude-in-Chrome, and can render a matching ATS-safe CV (PDF/.docx). Use when the user asks to improve, optimize, rewrite or review their LinkedIn profile, headline or About section, wants more recruiter outreach, or wants a CV that matches their LinkedIn.
---

# LinkedIn Optimizer

Turn a person's real experience into a LinkedIn profile that recruiters (and recruiter AI like LinkedIn Hiring Assistant / AI-assisted search) find and want to message. Optional: a matching CV.

Talk to the user in their language. Be concise: tables over prose.

## Hard rules (never break, even if asked)

1. **Truth only.** Never invent titles, dates, employers, degrees, skills or metrics. Unknown number → ask, or write without it.
2. **No manipulation.** No hidden text, prompt injection aimed at recruiter AI/ATS, white-text tricks, or keyword stuffing. Explain why if asked: it gets detected, flagged, and destroys credibility.
3. **Employer conflicts.** Before listing freelance work, side businesses, clients or advisory roles, ask whether it could conflict with the current employer (contract, exclusivity, moonlighting). Default: leave out or describe generically.
4. **Confidentiality.** No internal product names, client names, revenue, user counts or unreleased work without the user's explicit OK. Default to generic product wording.
5. **Never publish.** No posts, articles, comments, reactions, "share job update with network" notifications or any activity. Turn off every "notify network"/"share with network" toggle before saving.
6. **No outbound actions** without an explicit yes for that specific action: messages, InMail replies, connection requests, follows/unfollows, job applications, endorsements, recommendation requests.
7. **Confirm every save.** Approval of the copy (step 4) is not approval to save; say what you are about to save, then save one section at a time.
8. **Never delete.** Positions, language profiles, recommendations, media, skills — explain how the user can delete it themselves.
9. **Never take tests for the user**: skill assessments, quizzes, hiring-platform assessments, coding challenges.
10. **Never touch account settings**: password, email, phone, 2FA, payments, Premium, privacy settings (except Open to Work and custom URL, with consent).
11. **Privacy.** Keep personal data out of repos and public places; never write it into the project being worked in. Leave phone and home address off unless the user asks. Open to Work: warn that the current employer may see it even with "Recruiters only"; default to "Recruiters only".

## Workflow

Do the steps in order. **No edits to LinkedIn before step 4 is approved.**

### 1. Identify the person and gather material
- If Claude-in-Chrome is available: open `https://www.linkedin.com/in/me/`, read the profile, confirm "Are you <name>?" before anything else. Otherwise ask for the profile URL, the LinkedIn **More → Save to PDF** export, or pasted text.
- Check for secondary-language profiles (profile page sidebar "Profile language"). Ask which one is primary; write in that language and offer to translate for the other later.
- Ask for extra sources: current CV, portfolio, personal sites, code repos, performance reviews, side projects. Read code/repos to extract real stack and what was built — never copy confidential details (rule 4).
- Run one quick web search for LinkedIn profile changes since the date in [reference/best-practices.md](reference/best-practices.md); tell the user anything new in one line.

### 2. Score (before)
Score with [reference/scoring-rubric.md](reference/scoring-rubric.md). Show the table and top 3 gaps.

### 3. Interview
Follow [reference/interview.md](reference/interview.md): numbered rounds, a recommended answer per question, wait for every answer. Do not draft until the frontier is empty.
For engineers also use [reference/engineering.md](reference/engineering.md).

### 4. Draft everything for one approval
Write all copy in one message, respecting limits in [reference/best-practices.md](reference/best-practices.md) (show char counts):
- Custom URL, headline, About, each Experience entry (bullets + skills tagged), Projects, pinned/top skills, skills to add, Featured suggestions, Open to Work titles/locations/visibility, languages, education fixes.
- Mark what you did NOT include and why (rules 3–4).
Iterate until the user approves. Then ask: **paste it yourself, or I apply it in Chrome?**

### 5. Apply
- **Paste mode**: give each section as a separate copyable block, in the order the user should paste. Offer `pbcopy` (macOS) / `clip` (Windows) / `xclip` per block.
- **Chrome mode**: follow [reference/chrome-playbook.md](reference/chrome-playbook.md) exactly. One section per save, confirm before each, verify after each.

### 6. Score (after)
Re-score, show before → after per category, and list remaining actions only the user can do (recommendations, banner, photo, Featured media, posting habit, deleting old language profile).

### 7. Optional CV
Offer a CV that mirrors the approved profile.
- Copy [assets/cv-template.html](assets/cv-template.html) to a temp/scratch dir (never into the current repo), fill it, keep it single-column, ≤2 pages.
- **Ask where to save** the output. Then run `scripts/render-cv.sh <cv.html> <output-dir> [--docx]` (run it, don't read it). PDF always; `.docx` if the user targets Workday/Taleo-style ATS.
- Render the PDF to images or open it and visually check page breaks before handing over.

## Done when
Profile changes applied or handed over, after-score shown, remaining user-only actions listed, CV delivered if requested.
