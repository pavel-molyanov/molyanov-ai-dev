# Project Roadmap

<!--
This file tracks project development phases and timeline.

IMPORTANT: Do NOT add time estimates (weeks, months, dates) to phases.
Phases should be completion-criteria driven, not time-driven.
See project-planning skill for anti-patterns guidance.

WHEN TO FILL DETAILED:
- Phased development (MVP → v1.0 → v2.0)
- Migration projects (ALWAYS detailed)
- Complex projects (>10 features)
- Hard deadlines or constraints

WHEN MINIMAL IS FINE:
- Simple projects (<8 features)
- Building everything at once
- Solo developer, flexible timeline

Choose appropriate template below and delete others.
-->

---

## TEMPLATE 1: MINIMAL (for simple projects)

<!--
Use this if:
- Building all features at once
- Simple project, no phases
- No migration

DELETE TEMPLATES 2 and 3 below if using this.
-->

## Current Status

**Phase:** Initial Development
**Status:** Planning

---

## Development Plan

Building all features simultaneously. See [features.md](features.md) for complete feature list.

**Expected timeline:** [Estimate if known]

---

## Future Plans

[Optional: Ideas for after launch]

---

## TEMPLATE 2: PHASED (for complex greenfield projects)

<!--
Use this if:
- Multiple phases planned
- >10 features
- Clear MVP → Growth → Polish progression

DELETE TEMPLATES 1 and 3 if using this.
-->

## Current Status

**Phase:** Phase 0 - Planning
**Status:** Defining MVP scope

---

## Phase 1: [Phase Name, e.g., "Foundation"]

**Goal:** [What this phase achieves]

**Features:**
- [Feature #1]
- [Feature #2]
- [Feature #3]

**Milestone:** [How you know this phase is done]

**Success criteria:**
- [Specific measurable criterion]
- [Another criterion]

---

## Phase 2: [Phase Name]

**Goal:** [What this phase achieves]

**Features:**
- [Feature #4]
- [Feature #5]

**Milestone:** [Completion criteria]

---

## Phase 3: [Phase Name]

**Goal:** [What this phase achieves]

**Features:**
- [Feature #6]
- [Feature #7]

**Milestone:** [Completion criteria]

---

## Future Considerations

[Optional: Features or improvements for post-launch]

---

## TEMPLATE 3: MIGRATION (for migration projects)

<!--
Use this if:
- Replacing existing system
- Have current users/data to migrate

DELETE TEMPLATES 1 and 2 if using this.
-->

## Migration Context

**Current system:** [Name of system being replaced]

**Why migrate:**
- [Reason 1]
- [Reason 2]
- [Reason 3]

**Business constraints:**
- **Users:** [Number of active users]
- **Revenue:** [Monthly revenue / business criticality]
- **Downtime tolerance:** [How much downtime acceptable]
- **Timeline:** [Hard deadline if any]

**Migration risks:**
- [Risk 1]
- [Risk 2]
- [Risk 3]

---

## Phase 0: Foundation

**Goal:** Build core functionality

**Deliverables:**
- [Core feature 1]
- [Core feature 2]
- [Core feature 3]

**Milestone:** New system has feature parity for critical functions

---

## Phase 1: Migration Preparation

**Goal:** Ready for user migration

**Deliverables:**
- Data export from old system validated
- Import scripts tested
- Parallel testing with subset of users
- Monitoring and alerting configured

**Milestone:** Successfully migrated 10 test users

---

## Phase 2: Migration Execution

**Goal:** Move all users to new system

**Pre-migration checklist:**
- [ ] All critical features tested
- [ ] Data export validated
- [ ] Rollback plan documented
- [ ] Users notified 1 week in advance
- [ ] Support team prepared

**Migration steps:**
1. Announce maintenance window
2. Stop accepting new data in old system
3. Export final data
4. Import to new system
5. Verify data integrity
6. Switch webhooks/DNS to new system
7. Monitor for 48 hours

**Rollback triggers:**
- [Condition that triggers rollback]
- [Another condition]

**Rollback plan:**
1. [Step to revert to old system]
2. [Step to restore access]
3. [Step to communicate with users]

---

## Phase 3: Post-Migration

**Goal:** Add features not in old system

**Features:**
- [New feature 1]
- [New feature 2]
- [New feature 3]

**Milestone:** New features live and adopted

---

## Success Metrics

**Migration success:**
- [ ] Zero data loss
- [ ] Downtime < [X hours]
- [ ] User retention > [X]%
- [ ] No critical bugs
- [ ] Support tickets < [X] per day

**Post-migration KPIs:**
- [Metric 1 to track]
- [Metric 2 to track]

---

## Assumptions & Dependencies

**Key assumptions:**
1. [Assumption 1]
2. [Assumption 2]

**External dependencies:**
1. [Dependency 1]
2. [Dependency 2]

**What could change this plan:**
- [Factor that might require replanning]
- [Another factor]

---

<!--
END OF TEMPLATES

Instructions:
1. Choose appropriate template (Minimal / Phased / Migration)
2. Delete other templates and these comments
3. Fill in your specific information
4. Adjust phases based on your project's needs
-->
