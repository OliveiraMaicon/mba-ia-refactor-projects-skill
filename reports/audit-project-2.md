================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Node.js/JavaScript
Framework:     Express 4.18.2
Dependencies:  sqlite3, bcrypt, dotenv
Domain:        LMS API (cursos, matriculas, pagamentos, checkout)
Architecture:  Monolítica — God Class AppManager.js contém DB init, rotas e toda lógica de negócio
Source files:  3 files analyzed
DB tables:     users, courses, enrollments, payments, audit_logs
================================
================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 5 | LOW: 3

## Findings

### [CRITICAL] Hardcoded Secrets (AP-01)
File: src/utils.js:1-7
Description: The config object contains hardcoded production credentials: `dbUser: "admin_master"`, `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"`, and `smtpUser: "no-reply@fullcycle.com.br"`.
Impact: All production secrets are exposed in version control. Anyone with repository access can access the payment gateway and database.
Recommendation: Move all secrets to environment variables. Create a `.env.example` file with placeholder values.

### [CRITICAL] God Class (AP-03)
File: src/AppManager.js:4-139
Description: The `AppManager` class handles database initialization, schema creation, seed data, route setup, checkout processing, financial reporting, and user deletion — all in a single 139-line class.
Impact: Impossible to test individual components. Any change to payment logic risks breaking the report generation.
Recommendation: Split into separate modules for DB setup, business logic (controllers), and route definitions.

### [CRITICAL] Weak Cryptography — Custom Hash Function (AP-06)
File: src/utils.js:17-23
Description: The `badCrypto()` function loops 10,000 times generating repeated base64 substrings of the password, returning only the first 10 characters as the "hash".
Impact: Passwords are trivially crackable. This is not real hashing — it's deterministic encoding with truncation.
Recommendation: Replace with bcrypt. Add `bcrypt` package, use `bcrypt.hash()` and `bcrypt.compare()`.

### [HIGH] Sensitive Data in Logs (AP-20)
File: src/AppManager.js:45
Description: The checkout handler logs the payment gateway key to console: `console.log("Processando cartão ${cc} na chave ${config.paymentGatewayKey}")`.
Impact: Payment gateway key exposed in application logs, which may be aggregated in log management systems.
Recommendation: Never log API keys or secrets. Remove from console.log.

### [HIGH] No Password Validation (AP-10)
File: src/AppManager.js:28-36
Description: The checkout endpoint accepts a `pwd` field but uses a default password `"123456"` if none is provided. There is no validation of password strength.
Impact: Users can be created with empty or default passwords. The default fallback `"123456"` is hardcoded.
Recommendation: Require password, validate minimum length (≥8 chars), and hash with bcrypt.

### [HIGH] Business Logic in Routes (AP-07)
File: src/AppManager.js:28-78
Description: The checkout POST handler is 50 lines of deeply nested logic including user lookup, payment processing, enrollment creation, and audit logging — all inline.
Impact: Cannot test checkout logic independently of HTTP layer. Nested callbacks make error handling nearly impossible.
Recommendation: Extract to a CheckoutController with separate model/service calls. Flatten with async/await.

### [MEDIUM] Callback Hell / Nested Pyramid (AP-15)
File: src/AppManager.js:37-77,80-128
Description: The checkout handler has 5 levels of nested callbacks. The financial report has callback ladders through courses → enrollments → users → payments.
Impact: Extremely difficult to debug, modify, or reason about. Error handling is scattered and inconsistent at each nesting level.
Recommendation: Convert to async/await pattern using promisified database operations.

### [MEDIUM] N+1 Query Problem (AP-08)
File: src/AppManager.js:80-128
Description: The financial report fetches all courses, then loops over each executing separate queries for enrollments, then per enrollment queries for user data, then per user queries for payment data.
Impact: With 2 courses and 1 enrollment each, this generates ~6 database round-trips. Scales linearly with data growth.
Recommendation: Use JOINs to fetch all related data in fewer queries, or batch the secondary lookups.

### [MEDIUM] Missing CASCADE on Delete (AP-12)
File: src/AppManager.js:131-136
Description: Deleting a user runs only `DELETE FROM users` but leaves orphan records in enrollments and payments tables. The response message acknowledges: "as matrículas e pagamentos ficaram sujos no banco."
Impact: Orphan records accumulate over time, causing referential integrity violations and incorrect report data.
Recommendation: Use CASCADE delete or manually clean up child records in a transaction.

### [MEDIUM] Global Mutable State (AP-11)
File: src/utils.js:9-10
Description: `let globalCache = {}` and `let totalRevenue = 0` are module-level mutable variables modified by `logAndCache()`.
Impact: Cache grows unbounded (memory leak), shared across all requests (data leak), not thread-safe.
Recommendation: Remove global cache or use an external caching service like Redis with TTL.

### [MEDIUM] Inconsistent Error Responses (AP-19)
File: src/AppManager.js:35,38,41,50,54,70
Description: Error responses mix plain text (`res.send("Bad Request")`) with JSON (`res.status(500).send("Erro DB")`). Client cannot parse responses uniformly.
Impact: Frontend consumers must handle inconsistent response formats, leading to parsing errors.
Recommendation: Always return JSON: `res.status(400).json({ error: "message" })`.

### [LOW] Poor Variable Naming (AP-17)
File: src/AppManager.js:29-33
Description: Variables are abbreviated to single/two letters: `u` (user name), `e` (email), `p` (password), `cid` (course_id), `cc` (credit card). `enrId` and `enrPending` also use obscure abbreviations.
Impact: Very low readability. A new developer has no way to understand what `cc` or `cid` means without tracing back.
Recommendation: Use descriptive names: `userName`, `userEmail`, `password`, `courseId`, `cardNumber`.

### [LOW] Magic Numbers (AP-18)
File: src/utils.js:19
Description: The `badCrypto()` function loops exactly `10000` times and truncates to `10` characters — arbitrary constants with no named explanation.
Impact: These numbers have no clear meaning. If hash strength needs adjustment, the developer must find and understand the magic values.
Recommendation: Use a proper hashing library (bcrypt) which handles iteration counts internally with defaults.

### [LOW] No Input Validation on Checkout (AP-10)
File: src/AppManager.js:28-36
Description: The checkout endpoint checks only for presence of `usr`, `eml`, `cid`, `cc` but does not validate email format, credit card format, or password strength.
Impact: Malformed data stored in database, invalid transactions processed.
Recommendation: Add validation for email format (regex), credit card (Luhn check), and password (min length).

================================
Total: 14 findings
================================
