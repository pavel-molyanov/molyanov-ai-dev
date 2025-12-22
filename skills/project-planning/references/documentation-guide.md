# Documentation Creation Guide

This guide explains how to create project.md, features.md, and roadmap.md based on project characteristics.

---

## Always Fill All Three Files

**Important:** All three files (`project.md`, `features.md`, `roadmap.md`) already exist in project template (copied by `/init-project`). Your job is to fill them.

**If files don't exist** (old project):
Copy from template:
```bash
cp ~/.claude/shared/templates/new-project/.claude/skills/project-knowledge/guides/project.md .claude/skills/project-knowledge/guides/
cp ~/.claude/shared/templates/new-project/.claude/skills/project-knowledge/guides/features.md .claude/skills/project-knowledge/guides/
cp ~/.claude/shared/templates/new-project/.claude/skills/project-knowledge/guides/roadmap.md .claude/skills/project-knowledge/guides/
```

**For simple projects:**
- project.md will be concise (3-5 key features listed)
- features.md will be short (3-5 features detailed)
- roadmap.md can be left minimal or mostly empty

**For complex projects:**
- project.md will still be concise (high-level only)
- features.md will be detailed with grouping
- roadmap.md will have phases and milestones

---

## project.md Structure

### Purpose

High-level overview for understanding WHAT the project is and WHY it exists. Should be concise - details belong in features.md.

### Basic Structure (All Projects)

```markdown
# Project Context

## Project Overview
**Name:** [Project Name]
**Description:** [One-line description]
[Optional: 1-2 additional sentences with key context]

## Target Audience
**Primary users:** [Who uses this]
**Use case:** [Why they need it]

## Core Problem
[What pain point are we solving? 2-3 sentences]

## Key Features
[List 3-5 core capabilities only - high-level]
- **[Feature 1 name]** - [What it does in 1 sentence]
- **[Feature 2 name]** - [What it does in 1 sentence]
...

## Out of Scope
[What we explicitly DON'T do]
- [Thing 1 we don't support]
- [Thing 2 we don't support]
...
```

### Key Principles for project.md

**Keep it high-level:**
- Only 3-5 most important features (not exhaustive)
- One-line descriptions (details in features.md)
- Focus on WHAT and WHY, not HOW

**Specific target audience:**
- Not "everyone" or "users"
- Be specific: "Developers building CLI tools", "Small business owners"

**Clear out of scope:**
- Prevents scope creep
- Helps agents understand boundaries
- Examples: "No mobile app", "No real-time collaboration"

---

## features.md Structure

### Basic Structure (All Projects)

```markdown
# Features

Brief intro paragraph explaining project features.

## 1. [Feature Name]
**Priority:** [Critical | Important | Nice-to-have]
**Status:** [Planned | In Progress | Completed]
**Description:** [What it does and why]

[Optional: Dependencies, Technical notes]

## 2. [Next Feature]
...
```

### When to Group Features (>8 features)

If project has many features, group them logically:

```markdown
# Features

## Core Functionality

### 1. User Authentication
**Priority:** Critical
...

### 2. Data Management
**Priority:** Critical
...

## Admin & Operations

### 5. Admin Dashboard
**Priority:** Important
...

## Marketing & Growth

### 8. Email Campaigns
**Priority:** Nice-to-have
...
```

**Grouping strategies:**
- By user type (User features / Admin features)
- By subsystem (Core / Marketing / Analytics)
- By functional area (Authentication / Content / Communication)

### Feature Priorities

**Critical:**
- Blocks launch or migration
- Core user value
- Without it, product doesn't work

**Important:**
- Needed for smooth operation
- Major user value
- Can launch without it, but problematic

**Nice-to-have:**
- Enhances experience
- Secondary value
- Can easily wait for v2

### Dependencies

Only mention dependencies if they're NOT obvious:

```markdown
## 3. Payment Processing
**Dependencies:** User Authentication (#1)
[Obviously needs auth, but worth stating]

## 7. Email Notifications
**Dependencies:** None
[Can work independently]

## 9. Advanced Analytics
**Dependencies:** Data Collection (#4), User Tracking (#6)
[Multiple dependencies, worth listing]
```

---

## roadmap.md Decisions

### Always Fill, But...

**Minimal roadmap** (for simple projects):
```markdown
# Project Roadmap

## Current Status
**Phase:** Initial Development
**Status:** Planning

Building all features simultaneously.

## Feature List
See [features.md](features.md) for complete feature list and priorities.
```

**Detailed roadmap** (for complex/phased projects):
```markdown
# Project Roadmap

## Overview
[Migration context / phasing rationale]

## Phase 1: Foundation
**Goal:** Core functionality working
**Features:** #1, #2, #3, #4 (Critical features)
**Milestone:** Can create and manage basic data
**Exit criteria:** All Phase 1 features working, smoke tests pass

## Phase 2: User Experience
**Goal:** Production-ready user interface
**Features:** #5, #6, #7 (User-facing features)
**Milestone:** Complete user journey implemented
...
```

### When to Make Roadmap Detailed

Create detailed roadmap if ANY of these apply:

1. **Phased development**
   - User mentions MVP then v2
   - More than 10 features
   - Clear phases (foundation → features → polish)

2. **Migration project**
   - Existing system being replaced
   - Need detailed migration plan
   - Risk mitigation required

3. **Dependencies complex**
   - Features must be built in specific order
   - Multiple teams/stakeholders
   - Integration dependencies

4. **Timeline matters**
   - Hard deadlines
   - Revenue/business critical
   - Need to track progress

### When Minimal Is Fine

Minimal roadmap is appropriate if:
- Simple project (<8 features)
- Building everything at once
- Solo developer, flexible timeline
- No existing system to migrate from

**Ask user:** "Планируешь делать все сразу или поэтапно?"

---

## Migration Projects (Special Case)

Migration projects ALWAYS get detailed roadmap with special sections:

```markdown
# Migration Roadmap

## Migration Context
**Current system:** [Name]
**Why migrate:** [Reasons]
**Users:** [Count]
**Timeline:** [Constraints]

## Pre-Migration (Phase 0)
**Goal:** Ready for migration
- Feature parity achieved
- Data export validated
- Testing complete

## Migration (Phase 1)
**Goal:** Switch users to new system
**Steps:**
1. Announce maintenance window
2. Export final data
3. Import to new system
4. Verify integrity
5. Switch DNS/webhooks
6. Monitor 48h

**Rollback plan:**
[How to revert if problems]

## Post-Migration (Phase 2)
**Goal:** Add new features
[Features that weren't in old system]

## Risks & Mitigation
[Specific risks and how to handle]
```

---

## Content Guidelines

### Feature Descriptions

**Good:**
```markdown
## 1. Payment Processing
**Priority:** Critical
**Description:** Accept payments via Stripe for course purchases.
Supports one-time purchases and subscriptions. Handles webhooks for
payment confirmation and subscription updates.

**Technical notes:** Stripe API v2023-10, webhook verification required
```

**Bad (too vague):**
```markdown
## 1. Payments
Handle payments somehow
```

**Bad (too detailed):**
```markdown
## 1. Payment Processing
...
[10 paragraphs explaining Stripe API internals, code examples, etc.]
```

### Roadmap Milestones

**Good:**
```markdown
**Milestone:** Users can register, purchase courses, and watch videos

**Success criteria:**
- 10 test users complete full flow without issues
- Payment success rate >95%
- Video playback works on mobile and desktop
```

**Bad:**
```markdown
**Milestone:** Phase 1 done
```

---

## Examples by Project Type

### Simple Web App (5 features)

**features.md:**
- 5 features listed simply
- Clear priorities
- No grouping needed

**roadmap.md:**
- Minimal format
- "Building all at once"
- Reference to features.md

### SaaS Platform (15 features)

**features.md:**
- Features grouped by area (Core / Admin / Integrations)
- Detailed priorities
- Dependencies noted

**roadmap.md:**
- 3-4 phases
- MVP → Growth → Enterprise
- Milestones per phase

### Migration Project (any size)

**features.md:**
- Features marked: "Existing" vs "New"
- Migration tooling as separate feature
- Grouped by migration phase

**roadmap.md:**
- Detailed migration plan
- Pre-migration / Migration / Post-migration phases
- Risk mitigation section
- Rollback plan

---

## Common Mistakes

### Mistake 1: Features Too Granular

**Wrong:**
```
1. Create user button
2. User form validation
3. Save user to database
4. Show success message
```

**Right:**
```
1. User Management
   Complete CRUD for users
```

Features are user-facing capabilities, not implementation tasks.

### Mistake 2: No Priorities

**Wrong:**
```
## 1. Feature A
## 2. Feature B
## 3. Feature C
[All marked "Important"]
```

**Right:**
```
## 1. Feature A - Critical
## 2. Feature B - Nice-to-have
## 3. Feature C - Critical
```

If everything is critical, nothing is.

### Mistake 3: Timeline-Based Roadmap (AI-First Anti-Pattern)

**Wrong (timeline-based):**
```
Phase 1 (Week 1): Build entire CRM with 15 features
Phase 2 (Week 2): Launch to production
```
Problems: AI development pace is unpredictable. Time estimates create false expectations.

**Wrong (still timeline-based):**
```
Phase 1 (Months 1-2): Core CRM
Phase 2 (Month 3): Testing
```
Better, but still uses time estimates.

**Right (milestone-based):**
```
Phase 1: Core CRM Foundation
- Features: 5 critical features (#1-5)
- Milestone: Basic CRUD operations working
- Exit criteria: All critical features tested, smoke tests pass

Phase 2: Admin & Testing
- Features: 4 admin features (#6-9)
- Milestone: Admin can manage all data
- Exit criteria: E2E tests pass, ready for beta

Phase 3: Launch Preparation
- Features: Remaining features (#10-15)
- Milestone: Production-ready
- Exit criteria: Full test suite passes, documentation complete
```
Focus on WHAT and in WHAT ORDER, not WHEN.

### Mistake 4: Bloated Roadmap for Simple Project

**Wrong (for 3-feature todo app):**
```
# Roadmap

## Phase 0: Planning
- Requirements gathering
- User research
- Competitive analysis

## Phase 1: Foundation
- Database design
- API architecture
...
[5 pages of phases for simple app]
```

**Right:**
```
# Roadmap

Building all 3 features simultaneously.

See features.md for priority order and status.
```

---

## Quick Decision Tree

```
Q: How many features?
A: <5 features → Simple format
A: 5-10 features → Standard format, maybe group
A: >10 features → Grouped format

Q: Phased development?
A: Yes → Detailed roadmap with phases
A: No → Minimal roadmap

Q: Migration?
A: Yes → Always detailed roadmap + migration sections
A: No → Follow normal decision tree

Q: Complex dependencies?
A: Yes → Note in features.md, reflect in roadmap phases
A: No → Simple priority-based approach
```

---
