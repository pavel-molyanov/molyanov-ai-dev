# Documentation Structure Reference

This file describes the 11 core documentation files in `.claude/skills/project-knowledge/guides/`, their purpose, sections, and what information belongs in each.

## 1. project.md

**Purpose:** High-level project overview for understanding project goals and scope.

**Key Sections:**

### Project Name and Description
- One-sentence project description
- Brief explanation of what problem it solves

### Target Audience / Users
- Who will use this project
- Primary user personas
- User needs being addressed

### Core Features
- Main functionality (what's IN scope)
- Key capabilities
- Must-have features for MVP/launch

### Out of Scope
- What the project explicitly does NOT do
- Features postponed to later versions
- Common misconceptions to avoid

### Success Criteria
- How to measure project success
- Key metrics or outcomes
- Definition of "done"

**What to Include:**
- Business context and goals
- User-facing feature list
- Clear scope boundaries

**What to Avoid:**
- Technical implementation details (goes in architecture.md)
- Code examples or API specs
- Database schema (goes in database.md)

---

## 2. features.md

**Purpose:** Complete feature inventory with priorities, dependencies, and tracking.

**Key Sections:**

### Feature List
- All features with unique IDs/numbers
- Clear feature names
- Brief descriptions

### Per Feature:
- **Priority:** Critical / Important / Nice-to-have
- **Status:** Planned / In Progress / Completed
- **Description:** What it does and why (user value)
- **Dependencies:** Other features needed first (optional)
- **Technical notes:** Constraints or key decisions (optional)

### Grouping (for >8 features):
- Group by functional area (Core / Admin / Marketing)
- Group by user type (User features / Admin features)
- Group by subsystem

**What to Include:**
- User-facing capabilities (not implementation tasks)
- Why each feature is needed
- Priority rationale
- Dependencies between features

**What to Avoid:**
- Implementation tasks ("Create button", "Add validation")
- Code details (goes in code comments or patterns.md)
- Granular TODO items (features are capabilities, not tasks)

---

## 3. roadmap.md

**Purpose:** Development phases, timeline, and migration plan (if applicable).

**Three Formats:**

### Minimal (simple projects):
- Current status
- "Building all features at once"
- Reference to features.md

### Phased (complex greenfield):
- Phase breakdown (Phase 1, 2, 3...)
- Goal and features per phase
- Milestones and success criteria
- Timeline estimates

### Migration (replacing existing system):
- Migration context (current system, why migrate, users, risks)
- Pre-migration phase
- Migration execution plan
- Post-migration phase
- Rollback plan
- Success metrics

**What to Include:**
- How development is structured
- Major milestones
- For migrations: detailed migration strategy and risks
- Dependencies between phases

**What to Avoid:**
- Day-to-day task tracking (use work/ folder for that)
- Detailed implementation plans (those go in tech-spec)
- Bloated roadmap for simple projects (keep minimal)

---

## 4. architecture.md

**Purpose:** Technical architecture, tech stack, and system design.

**Key Sections:**

### Tech Stack
- Programming languages with versions
- Frameworks and libraries with versions
- Runtime environments (Node.js, Python, etc.)
- **Why chosen:** Brief justification for major tech decisions

### Project Structure
- Key directories and their purpose
- File organization patterns
- Module/package structure
- Where different types of code live

### Dependencies
- Critical external dependencies
- Why specific libraries were chosen
- Version constraints or requirements
- Dependency management strategy

### External Integrations
- Third-party APIs used
- External services (Stripe, Auth0, etc.)
- Integration points and protocols
- Authentication mechanisms

### Data Flow
- High-level system architecture
- Request/response flow
- Key architectural patterns (MVC, microservices, etc.)
- Component interactions

**What to Include:**
- Project-specific architectural decisions
- References to key implementation files
- Integration architecture
- Tech stack rationale

**What to Avoid:**
- Generic "what is React" explanations
- Code examples (use file references)
- Database schema details (goes in database.md)
- Deployment specifics (goes in deployment.md)

---

## 5. patterns.md

**Purpose:** Coding standards, conventions, and project-specific best practices.

**Special Structure:**

This file has TWO distinct sections:

### Universal Patterns (from template)
- **Source:** Comes from `~/.claude/shared/templates/new-project/.claude/skills/project-knowledge/guides/patterns.md`
- **Purpose:** Common best practices shared across all projects for consistent code quality
- **Content:** Naming conventions, code organization, error handling, security, testing, code quality guidelines
- **Important:** This section is intentionally generic and should NOT be removed or modified
- **Applies to:** All projects regardless of tech stack or domain

### Project-Specific Patterns (custom for this project)
- **Purpose:** Document patterns unique to this project
- **Content:** Framework-specific conventions, domain naming, external integrations, database patterns, team conventions
- **Can be empty:** For simple projects, only Universal Patterns may be sufficient

**Key Sections in Universal Patterns:**
- Naming Conventions (functions, variables, files, classes)
- Code Organization (file responsibility, function size, nesting limits)
- Separation of Concerns (config, messages, prompts, business logic)
- Security (secrets, validation, sanitization)
- Error Handling (try-catch, logging, fail fast)
- Testing (public APIs, mocking, test naming)
- Code Quality (comments, DRY, readability)

**What to Add to Project-Specific Section:**
- Framework-specific conventions (React hooks, Django patterns, etc.)
- Domain terminology and naming (Order/Cart vs Purchase/Basket)
- External integration patterns (Stripe, SendGrid, AWS usage)
- Database-specific patterns (transactions, migrations, query optimization)
- Team conventions (PR process, commit format)

**What to Avoid:**
- Removing Universal Patterns (they're intentional template content)
- Adding generic advice to Project-Specific section
- Code examples (reference actual code files instead)
- Duplicating content between sections

---

## 6. database.md

**Purpose:** Data models, schema, and database architecture.

**Key Sections:**

### Database Type
- SQL, NoSQL, or other
- Specific database (PostgreSQL, MongoDB, etc.)
- Version and key features used

### Tables/Collections
- Main entities and their purpose
- Key fields for each entity
- Data types and constraints
- Relationships between entities

### Constraints and Indexes
- Primary keys and foreign keys
- Unique constraints
- Indexes for performance
- Validation rules

### Migration Strategy
- How schema changes are managed
- Migration tool (Prisma, Alembic, etc.)
- Rollback procedures
- Seeding strategy

### Sensitive Data
- What data is sensitive
- Encryption approach
- Access controls
- PII handling

**What to Include:**
- Schema overview (not full SQL dumps)
- Important relationships and constraints
- Migration approach
- References to schema files or migration directories

**What to Avoid:**
- Full table definitions (reference migration files)
- Generic database concepts
- SQL tutorial content
- Sample queries (unless project-specific and complex)

---

## 7. deployment.md

**Purpose:** Deployment infrastructure, environments, and operational procedures.

**Key Sections:**

### Deployment Platform
- Hosting provider (Vercel, AWS, Heroku, etc.)
- Infrastructure setup (serverless, containers, VPS)
- Regions and availability

### SSH/Access Information
- How to access servers (if applicable)
- SSH key locations
- VPN requirements
- Access control procedures

### Environment Variables
- **Names only** (never values!)
- Purpose of each variable
- Required vs optional
- Where to set them (locally, CI/CD, platform)

### Deployment Triggers
- What triggers deployments
- Branch → environment mapping
- CI/CD pipeline overview
- Manual deployment procedures

### Rollback Procedures
- How to rollback a deployment
- Rollback triggers
- Data migration rollback strategy

**What to Include:**
- Platform-specific configuration
- Environment variable names and purposes
- CI/CD workflow overview
- References to config files (vercel.json, Dockerfile, etc.)

**What to Avoid:**
- Actual secret values
- Generic platform documentation
- Full CI/CD config dumps (reference files)
- Obvious information ("deploy to production is automatic")

---

## 8. git-workflow.md

**Purpose:** Git branching strategy and development workflow.

**Key Sections:**

### Branch Structure
- Main branch (main/master)
- Development branches
- Feature branch naming
- Release branch strategy

### Branch Decision Criteria
- When to create a new branch
- When to merge directly
- Feature flags vs feature branches
- Hotfix procedures

### Testing Requirements
- What tests must pass before merge
- Local testing requirements
- CI/CD testing gates
- Manual testing checklist

### Security Gates
- Pre-commit hooks
- Secret scanning
- Security checks before merge
- Code review requirements

**What to Include:**
- Project-specific branching strategy
- Merge requirements
- References to CI/CD configs

**What to Avoid:**
- Git basics ("git commit creates a commit")
- Generic git workflows (unless customized)
- Full CI/CD pipeline details (reference deployment.md)

---

## 9. ux-guidelines.md

**Purpose:** User experience, interface guidelines, and content standards.

**Key Sections:**

### Interface Language
- Primary language (English, Russian, etc.)
- Localization strategy if multilingual
- Language switching approach

### Tone of Voice
- Formal vs informal
- Brand personality
- User communication style
- Error message tone

### Domain Glossary
- Domain-specific terms and definitions
- Preferred terminology
- Terms to avoid
- Abbreviations and acronyms

### Text Patterns
- Button text conventions
- Form labels and placeholders
- Success/error message templates
- Help text patterns

### Design System
- Component library used (if any)
- Color scheme references
- Typography standards
- Spacing and layout conventions

**What to Include:**
- Project-specific UX decisions
- Domain terminology unique to project
- Content guidelines
- References to design files or component libraries

**What to Avoid:**
- Generic UX principles
- Full design system documentation (reference it)
- Component code examples
- Obvious UI patterns

---

## 10. monitoring.md

**Purpose:** Observability infrastructure - logging, error tracking, metrics, and production monitoring.

**Key Sections:**

### Logging
- Where logs are stored (stdout, CloudWatch, local files)
- Log format (JSON structured, plain text, framework default)
- Log retention policy
- Log levels used

### Error Tracking
- Error tracking tool (Sentry, Rollbar, none)
- Configuration status and credentials location
- What errors are tracked
- Which environments monitored

### Metrics (Optional)
- Analytics tools (Google Analytics, Vercel Analytics)
- Performance tracking approach
- Key metrics monitored (response time, error rate, etc.)

### Health Checks (Optional)
- Health check endpoints
- What they verify (DB connectivity, external APIs)
- Used by (Docker, load balancer, monitoring)

### Alerts (Optional)
- Alerting tool and configuration
- Alert rules and thresholds
- Alert recipients

**What to Include:**
- Actual tools and services used
- Where credentials/config stored (.env variables)
- Retention and sampling policies
- Production vs staging differences

**What to Avoid:**
- General monitoring best practices
- Tool documentation (link to it)
- Implementation details (how to add logging statements)
- Obvious information ("logs help debug issues")

---

## 11. business-rules.md

**Purpose:** Domain-specific business logic, workflows, validation rules, and calculations that aren't obvious from code.

**Key Sections:**

### Multi-step Workflows
- State transitions and flow
- Valid state changes
- Conditions for transitions
- Rules for cancellations/refunds

### Validation Rules
- Business constraints (time windows, limits, restrictions)
- Complex validation logic
- Edge cases and special conditions

### Calculations/Formulas
- Pricing calculations
- Commission or fee structures
- Discount application logic
- Tax calculation rules

### State Machines
- Entity lifecycle states
- Transition triggers and conditions
- Time-based state changes

### Access Control (Optional)
- Feature access by tier/role
- Content visibility rules
- Permission inheritance

**What to Include:**
- Domain-specific rules not obvious from code
- Business constraints with rationale
- Formulas with component explanation
- Workflows with state diagrams in text

**What to Avoid:**
- Technical implementation details (use patterns.md)
- Database constraints (use database.md)
- Generic validation ("email must be valid")
- Obvious business logic

**Note:** This file is optional. Delete if project has simple CRUD logic or no complex domain rules.

---

## General Guidelines for All Files

### File Organization
- Use clear heading hierarchy (##, ###)
- Keep related information together
- Use consistent formatting across files

### Cross-References
- Reference other documentation files when relevant
- Link to actual code files instead of duplicating code
- Point to external documentation for frameworks/libraries

### Maintenance
- Update when project changes
- Remove outdated information immediately
- Keep concise - delete unnecessary details
- Verify consistency across files

### Language
- All documentation in English (even for Russian-language projects)
- Use clear, technical language
- Avoid marketing language
- Be specific and actionable
