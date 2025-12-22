# Legacy Code Research

## Purpose
This file documents findings from analyzing existing legacy code in `old/` folder. Helps Agent understand current state before creating context.

## What goes here

### Project Overview
- What does the project do (core functionality)
- What problem it solves
- Current users/use cases (if known)
- Project history (age, team size, maintenance status)

### File Structure Tree
- Complete directory tree of the project
- Key folders and their purposes
- File organization patterns
- Notable file locations (configs, entry points, tests)

### Architecture Analysis
- Overall architecture pattern (monolith, microservices, MVC, etc.)
- Folder structure and organization
- Entry points (main files, routes)
- Key modules and their responsibilities
- Data flow (how components interact)

### API Endpoints
- List all API endpoints (REST, GraphQL, etc.)
- HTTP methods and paths
- Request/response formats
- Authentication requirements
- API versioning approach (if any)

### Tech Stack & Dependencies
- Programming languages and versions
- Frameworks and libraries used
- Database (type, schema approach)
- External services/APIs integrated
- Build tools and package manager

### Database Schema
- Database type and version
- Tables/collections and their purposes
- Key fields and data types
- Relationships between entities
- Indexes and constraints
- Migration strategy (if exists)

### Configuration Files Details
- All configuration files found (package.json, docker-compose.yml, etc.)
- Build configuration (webpack, vite, rollup, etc.)
- Deployment configuration
- Environment-specific configs
- Scripts & commands (npm/yarn scripts, Makefile, etc.)

### Environment Variables
- All environment variables from .env.example or similar
- Required vs optional variables
- Default values (if specified)
- Purpose of each variable
- Sensitive variables that need secrets management

### Code Patterns Found
- Common patterns used in codebase
- Code organization approaches
- Naming conventions
- Error handling approach
- Testing approach (if any tests exist)

### Code Quality Assessment
- Does code follow separation of concerns?
- Are there hardcoded values (API keys, URLs, magic numbers)?
- Is configuration externalized?
- Code readability and maintainability
- Documentation quality
- Test coverage

### Secrets & Sensitive Data
- Hardcoded secrets found in code (API keys, tokens, passwords)
- Secrets in configuration files
- .env.example analysis (what secrets are needed)
- Database credentials handling
- Third-party service credentials
- Recommendations for secrets management

### Problems & Technical Debt
- Security issues (hardcoded secrets, SQL injection risks, etc.)
- Performance bottlenecks
- Missing error handling
- Code duplication
- Outdated dependencies
- Missing tests
- Documentation gaps

### Migration Recommendations
- What can be reused as-is
- What needs refactoring before use
- What should be rewritten from scratch
- Priority order for migration/refactoring
- Estimated complexity (low/medium/high)

---

Keep it factual and objective. Focus on understanding the code, not judging previous developers.
