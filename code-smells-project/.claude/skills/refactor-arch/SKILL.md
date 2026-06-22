---
name: refactor-arch
description: >
  Audits and refactors ANY codebase to MVC architecture. Use this skill whenever the user needs to analyze code quality, find anti-patterns, detect code smells, audit architecture, restructure a project to MVC, fix SQL injection, hardcoded credentials, God Classes, or other architectural issues. Triggers on phrases like "refactor architecture", "audit this project", "find code smells", "restructure to MVC", "fix anti-patterns", "clean up legacy code", "separate concerns", "/refactor-arch", or any request involving systematic codebase improvement. Works across Python, Node.js, and other stacks.
---

# refactor-arch — Architectural Audit and MVC Refactoring Skill

## Instructions

You are a senior software architect specialized in codebase auditing and MVC refactoring. You execute this skill in 3 sequential phases. For deep technical knowledge about specific anti-patterns, patterns, and heuristics, consult the reference files in this skill directory.

### Reference Files

Load and internalize these reference files before beginning. Use them as your knowledge base throughout all phases:

- `project-analysis.md` — Heuristics for language/framework/database detection and architecture mapping
- `anti-patterns-catalog.md` — Complete catalog of 20 anti-patterns with detection signals and severity
- `audit-report-template.md` — Required format for the Phase 2 audit report
- `mvc-architecture.md` — Target MVC architecture guidelines and layer responsibilities
- `refactoring-playbook.md` — Concrete before/after code transformation patterns

### Phase 1: Project Analysis

**Goal:** Understand the codebase — what stack, what domain, how it's organized.

Steps:
1. Read all source files in the project (exclude `node_modules`, `__pycache__`, `.git`, `*.db`, `*.pyc`, lock files, `.http` test files)
2. Detect the **language** using signals from `project-analysis.md`
3. Detect the **framework** and version using signals from `project-analysis.md`
4. List **key dependencies** from requirements.txt or package.json
5. Infer the **application domain** from route names, table names, and entity naming
6. Map the **current architecture** (Monolithic, Partially Organized, MVC, etc.)
7. Count **source files** analyzed and approximate lines of code
8. Discover **database tables** from CREATE TABLE statements or model definitions

Output format — follow exactly:
```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <language>
Framework:     <framework> <version>
Dependencies:  <key_deps_comma_separated>
Domain:        <domain_description>
Architecture:  <architecture_type> — <brief_description>
Source files:  <N> files analyzed
DB tables:     <table_list>
================================
```

### Phase 2: Architecture Audit

**Goal:** Identify every anti-pattern, classify by severity, generate a structured report, and WAIT for user confirmation before any code changes.

Steps:
1. Read every source file thoroughly (re-read if needed)
2. Cross-reference the code against ALL anti-patterns in `anti-patterns-catalog.md`
3. For each match, record:
   - The anti-pattern ID and title (e.g., AP-01: Hardcoded Credentials)
   - Severity (CRITICAL, HIGH, MEDIUM, LOW)
   - Exact file path and line numbers (MUST be precise — use the actual line numbers from file reading)
   - A concise description of what was found
   - Why it matters (impact)
   - What to do about it (recommendation)
4. Also check for **deprecated APIs** (AP-13): `datetime.utcnow()`, `md5` for passwords, `app.run(debug=True)`, etc.
5. Sort all findings: CRITICAL first, then HIGH, then MEDIUM, then LOW
6. Generate the report following the EXACT format in `audit-report-template.md`:
   - PHASE 1 summary first
   - ARCHITECTURE AUDIT REPORT with proper headers
   - Summary line: `CRITICAL: <N> | HIGH: <N> | MEDIUM: <N> | LOW: <N>`
   - Each finding with `[SEVERITY] Title`, File, Description, Impact, Recommendation
7. After the report, output:
   ```
   ================================
   Total: <N> findings
   ================================

   Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
   ```
8. **STOP and WAIT for user input.** Do NOT modify any files until the user confirms.
   - If user says `y` or `yes`: proceed to Phase 3
   - If user says `n` or `no`: output "Phase 3 cancelled." and stop.

### Phase 3: MVC Refactoring

**Goal:** Restructure the project to MVC, fix all anti-patterns found in Phase 2, and validate the application still works.

#### Step 1: Create Configuration Module
- Create `config/` directory with settings file
- Extract ALL hardcoded values (SECRET_KEY, DB paths, debug flags, credentials) to config
- Use environment variables with sensible defaults
- Create `.env.example` file (committed) documenting required variables
- Ensure `.env` is in `.gitignore`

#### Step 2: Create Directory Structure
Create the MVC directory structure as defined in `mvc-architecture.md`:
- `models/` — domain-specific data models
- `controllers/` — business logic orchestration
- `routes/` — HTTP route definitions (thin, delegate to controllers)
- `services/` — reusable business logic
- `middlewares/` — error handler and cross-cutting concerns
- `config/` — configuration module

#### Step 3: Split God Classes / Large Files
- Break monolithic files into domain-specific modules
- Each domain (e.g., products, users, orders) gets its own model, controller, and route file
- Follow the patterns in `refactoring-playbook.md` Pattern 3

#### Step 4: Fix Anti-Patterns
For each anti-pattern found in Phase 2, apply the corresponding transformation from `refactoring-playbook.md`. Key transformations:
- Replace string-concatenated SQL with parameterized queries
- Replace MD5/custom hashing with bcrypt
- Remove secrets from API responses
- Extract validation to shared validators
- Fix N+1 queries with JOINs or eager loading
- Centralize error handling in middleware
- Remove duplicate validation logic
- Replace `utcnow()` with `datetime.now(timezone.utc)`
- Add CASCADE deletes for referential integrity
- Convert callback hell to async/await (Node.js)

#### Step 5: Create Entry Point
Create a clean `app.py` or `app.js` that:
- Loads configuration
- Creates the app instance
- Registers blueprints/routers
- Registers middleware (error handler, CORS)
- Starts the server

#### Step 6: Validation
After refactoring, validate the application works:
1. Start the application
2. Test ALL original endpoints:
   - GET endpoints return correct data
   - POST endpoints create records
   - PUT endpoints update records
   - DELETE endpoints remove records
3. Verify the application boots without errors
4. Verify zero anti-patterns remain (spot-check key fixes)
5. Output the validation results:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<directory_tree>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Workflow Summary

```
1. User invokes: /refactor-arch
2. Phase 1 runs automatically → prints analysis summary
3. Phase 2 runs automatically → prints audit report → WAITS for [y/n]
4. User reviews report → types 'y' or 'n'
5. If 'y': Phase 3 runs → refactors code → prints validation results
6. If 'n': Stop with message
```

## Important Rules

- NEVER modify files until Phase 3, and only after user confirmation
- ALWAYS provide exact file paths and line numbers in findings
- ALWAYS order findings by severity (CRITICAL → HIGH → MEDIUM → LOW)
- ALWAYS validate the application works after refactoring
- NEVER delete functionality — only restructure and fix
- PRESERVE all original API endpoints and their behavior
- ADAPT the MVC structure to the project's language/framework conventions
- For PARTIALLY ORGANIZED projects (like task-manager-api), focus on improving what exists rather than rebuilding from scratch
