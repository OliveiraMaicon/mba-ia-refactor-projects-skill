# Audit Report Template

This document defines the required format for the Phase 2 audit report.

## Report Structure

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <detected_language>
Framework:     <detected_framework> <version>
Dependencies:  <key_dependencies_comma_separated>
Domain:        <domain_description>
Architecture:  <architecture_type_with_brief_description>
Source files:  <N> files analyzed
DB tables:     <table_names_comma_separated>
================================
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <project_name>
Stack:   <language> + <framework>
Files:   <N> analyzed | ~<M> lines of code

## Summary
CRITICAL: <N> | HIGH: <N> | MEDIUM: <N> | LOW: <N>

## Findings

### [SEVERITY] <Title>
File: <filename>:<line_start>-<line_end>
Description: <1-2 sentence description of the issue>
Impact: <1 sentence on why this matters>
Recommendation: <concrete action to fix>

### [SEVERITY] <Title>
File: <filename>:<line_start>
Description: ...
Impact: ...
Recommendation: ...

[... more findings ...]

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

## Formatting Rules

1. **Severity ordering**: Findings MUST be ordered from CRITICAL → HIGH → MEDIUM → LOW
2. **File + line numbers**: Every finding MUST include exact file path and line number(s)
3. **Severity label**: Each finding title MUST be prefixed with `[CRITICAL]`, `[HIGH]`, `[MEDIUM]`, or `[LOW]`
4. **Description**: 1-3 concise sentences describing what was found
5. **Impact**: 1 sentence on practical impact — what breaks, what's at risk
6. **Recommendation**: Concrete, actionable guidance — what specifically to do
7. **Anti-pattern ID**: Optionally include the AP ID from the catalog: `(AP-01)` at end of title
8. **Total findings**: Final count inclui CONTAGEM REAL, not estimated

## Phase 2 Completion

After printing the report, the skill MUST pause and present:
```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```
Wait for user input. Only proceed on `y` or `yes`. On `n` or `no`, exit gracefully with `Phase 3 cancelled. Audit report saved.`
