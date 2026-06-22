# Anti-Patterns Catalog

Each anti-pattern includes: severity, detection signals, impact, and recommendation.

---

## AP-01: Hardcoded Credentials — CRITICAL

**Severity:** CRITICAL

**Detection signals:**
- String literals containing `secret`, `password`, `senha`, `key`, `token`, `api_key` assigned to config/constants
- Variables named `SECRET_KEY`, `DB_PASSWORD`, `API_KEY` with string literal values
- Config objects with `dbPass`, `dbUser`, `paymentGatewayKey`, `smtpUser` containing plaintext credentials
- Email credentials (`email_user`, `email_password`) hardcoded in source files

**Impact:** Exposes sensitive data in version control, security breach risk, impossible to rotate credentials without code change.

**Recommendation:** Extract all credentials to environment variables or a secure vault. Use `os.getenv()`, `process.env`, or `dotenv` files with `.env.example` committed and real `.env` in `.gitignore`.

---

## AP-02: SQL Injection (String Concatenation in Queries) — CRITICAL

**Severity:** CRITICAL

**Detection signals:**
- SQL queries built via string concatenation: `"SELECT * FROM x WHERE id = " + str(id)`
- String interpolation in SQL: `` `SELECT * FROM x WHERE name = '${name}'` ``
- Query building with `+=` appending user input strings
- `cursor.execute(query)` where `query` contains `+`, `%s` (Python), or template literals (JS) with user input
- No parameterized queries (`?` placeholders with parameter arrays)

**Impact:** Complete database compromise via injection attacks, data exfiltration, data destruction.

**Recommendation:** Always use parameterized queries. Python: `cursor.execute("SELECT * FROM x WHERE id = ?", (id,))`. Node.js: `db.get("SELECT * FROM x WHERE id = ?", [id], callback)`.

---

## AP-03: God Class / God Object — CRITICAL

**Severity:** CRITICAL

**Detection signals:**
- Single file/class exceeding 200 lines covering multiple business domains
- One class handling: database initialization + route setup + business logic + validation + response formatting
- File with functions for completely unrelated entities (products, users, orders, reports all in one file)
- Class with `initDb()`, `setupRoutes()`, financial logic, user management, and CRUD for multiple entities
- File/module name like `models.py` containing all domain logic regardless of entity

**Impact:** Impossible to test in isolation, any change affects everything, high coupling, difficult to maintain and extend.

**Recommendation:** Split into domain-specific modules. Each domain (product, user, order) gets its own model, controller, and route file.

---

## AP-04: Exposed Secrets in API Responses — CRITICAL

**Severity:** CRITICAL

**Detection signals:**
- Health check or status endpoints returning `secret_key`, passwords, or internal configuration
- `to_dict()` or serialization methods including password/hash fields in output
- API responses containing `config`, `secret`, `password` keys
- Debug information endpoints that dump internal state

**Impact:** Secrets exposed to any client hitting public endpoints, can be discovered by scanners.

**Recommendation:** Never return credentials in API responses. Remove `password`, `secret_key`, and internal config from response DTOs. Use dedicated serializers that explicitly exclude sensitive fields.

---

## AP-05: Arbitrary Query Execution Endpoint — CRITICAL

**Severity:** CRITICAL

**Detection signals:**
- Route/endpoint that accepts raw SQL string and executes it directly
- Parameters named `sql`, `query`, `raw_sql` that get passed to `cursor.execute()` or `db.run()`
- Admin endpoints without authentication that execute arbitrary DB commands

**Impact:** Complete database takeover, data destruction, privilege escalation.

**Recommendation:** Remove the endpoint entirely. If dynamic queries are needed, use a query builder with whitelisted operations.

---

## AP-06: Weak Cryptography / Deprecated Hash Functions — HIGH

**Severity:** HIGH

**Detection signals:**
- Use of MD5 for password hashing: `hashlib.md5()`, `crypto.createHash('md5')`
- Use of SHA1 for password hashing
- Custom/homebrew hashing functions (e.g., functions named `badCrypto`, `myHash`, `simpleHash`)
- Base64 encoding used as "encryption" or "hashing"
- Passwords stored without salt
- String repetition loops used as hashing

**Impact:** Passwords easily crackable with rainbow tables, vulnerable to brute force. MD5 has been cryptographically broken for years.

**Recommendation:** Use bcrypt, scrypt, argon2, or PBKDF2. Python: `werkzeug.security.generate_password_hash()` or `bcrypt`. Node.js: `bcrypt` package. Never use MD5 or SHA1 for password storage.

---

## AP-07: Business Logic in Routing Layer — HIGH

**Severity:** HIGH

**Detection signals:**
- Route handler functions exceeding 30 lines
- Validation logic (if/else chains checking fields) inside route definitions
- N+1 query loops inside route handlers
- Notification/push/email logic inside route handlers
- Business calculations (totals, discounts, stats) inside route handlers
- Overdue/completion logic duplicated in multiple routes

**Impact:** Violates Single Responsibility Principle, impossible to unit test business logic independently, duplicate code across routes.

**Recommendation:** Move business logic to service layer or controller classes. Routes should only handle HTTP concerns: parse request, call service, format response.

---

## AP-08: N+1 Query Problem — MEDIUM

**Severity:** MEDIUM

**Detection signals:**
- Database query inside a `for` loop iterating over another query's results
- Pattern: fetch list, then loop over list executing individual queries per item
- Multiple cursor/connection objects created inside loops
- `db.get()` or `cursor.execute()` calls nested inside `forEach()` or `for item in results:`

**Impact:** Severe performance degradation. 101 queries instead of 2 (1 for list + 1 per item). Exponentially worse with nested loops.

**Recommendation:** Use JOINs to fetch related data in a single query. For many-to-many, use batch queries with `WHERE id IN (...)` then map in application code.

---

## AP-09: Duplicated Validation Logic — MEDIUM

**Severity:** MEDIUM

**Detection signals:**
- Same validation rules (field required, min length, max length) repeated in create AND update handlers
- Identical if/else checks for field validation in multiple functions
- Status validation lists duplicated across files
- Priority validation range checks repeated

**Impact:** Changes to validation rules require updating multiple places, leading to inconsistencies and bugs.

**Recommendation:** Extract validation to a shared module, validation schema (Marshmallow, Pydantic, Joi, Zod), or model-level validation methods.

---

## AP-10: Missing Input Validation — MEDIUM

**Severity:** MEDIUM

**Detection signals:**
- Route handlers that directly use `request.get_json()` values without type checking
- No email format validation before storage
- No minimum/maximum length checks on string inputs
- Integer fields accepting any value including negative numbers
- No existence check for related entities (foreign key validation)

**Impact:** Data corruption, type errors, security vulnerabilities via malformed input.

**Recommendation:** Validate all inputs at the controller/route layer. Check types, ranges, formats, and referential integrity before passing to business logic.

---

## AP-11: Global Mutable State — MEDIUM

**Severity:** MEDIUM

**Detection signals:**
- Global/module-level variables that get mutated: `db_connection = None; global db_connection`
- `globalCache = {}`, `totalRevenue = 0` declared at module scope and modified by functions
- Singleton database connections with `check_same_thread=False` in SQLite
- In-memory caches without expiration or size limits

**Impact:** Thread safety issues, unpredictable behavior in concurrent requests, test isolation impossible, data leaks between requests.

**Recommendation:** Use dependency injection, application factory pattern, or request-scoped contexts. For caches, use Redis/memcached.

---

## AP-12: Missing CASCADE on Delete — MEDIUM

**Severity:** MEDIUM

**Detection signals:**
- DELETE route for parent entity without deleting child records
- Comments or code implying orphan records: "ficaram sujos no banco"
- No `ON DELETE CASCADE` in foreign key constraints
- Manual deletion of parent without iterating over related children

**Impact:** Orphan records accumulate, referential integrity broken, inflated storage and incorrect query results.

**Recommendation:** Use `ON DELETE CASCADE` in FK constraints, or delete child records in a transaction before deleting the parent.

---

## AP-13: Deprecated API Usage — MEDIUM

**Severity:** MEDIUM

**Detection signals:**
- `datetime.utcnow()` in Python — deprecated since Python 3.12, use `datetime.now(datetime.UTC)` or `datetime.now(timezone.utc)`
- `datetime.utcfromtimestamp()` — deprecated
- `sqlite3.connect(db, check_same_thread=False)` — not thread-safe for web apps
- `app.run(debug=True)` — deprecated for production, use WSGI server
- `hashlib.md5()` — cryptographically broken for password hashing (also AP-06)
- `Buffer.from().toString('base64')` used as crypto — not encryption
- `md5` / `sha1` from `crypto` module in Node.js — deprecated for security purposes

**Impact:** Security vulnerabilities, future compatibility breaks, suboptimal performance.

**Recommendation:** Replace with current API equivalents. Use `datetime.now(timezone.utc)` instead of `utcnow()`. Use WSGI servers (gunicorn, uwsgi) for deployment.

---

## AP-14: Hardcoded Debug Mode — HIGH

**Severity:** HIGH

**Detection signals:**
- `DEBUG = True` or `app.config["DEBUG"] = True` hardcoded in app.py
- `app.run(debug=True)`
- No environment-based configuration for debug mode
- Stack traces exposed in error responses from Flask debug mode

**Impact:** Detailed error pages with stack traces exposed to attackers, code disclosure, potential RCE through Werkzeug debugger in production.

**Recommendation:** Read debug mode from environment variable: `DEBUG = os.getenv("DEBUG", "false").lower() == "true"`. Default to False.

---

## AP-15: Callback Hell / Nested Pyramid — MEDIUM

**Severity:** MEDIUM (Node.js specific)

**Detection signals:**
- 4+ levels of nested callbacks in async JavaScript
- Pattern: `db.get(..., () => { db.get(..., () => { db.run(..., () => { ... }) }) })`
- Deep nesting in route handlers making code flow hard to follow

**Impact:** Extremely difficult to debug and maintain, error handling scattered at each level, "callback hell" anti-pattern.

**Recommendation:** Use async/await with promise-based database drivers, or extract nested operations into named functions.

---

## AP-16: Print Statements for Logging — LOW

**Severity:** LOW

**Detection signals:**
- `print()` statements used instead of proper logging framework
- `console.log()` without log levels
- Log messages containing sensitive data (emails, passwords, credit card partials)

**Impact:** No log level control, no structured logging, no log rotation, potential exposure of PII in logs.

**Recommendation:** Use `logging` module (Python) or `winston`/`pino` (Node.js) with appropriate log levels. Never log credentials or PII.

---

## AP-17: Poor Variable Naming — LOW

**Severity:** LOW

**Detection signals:**
- Single-letter or two-letter variable names for non-trivial values: `u`, `e`, `p`, `cc`, `cid`
- Abbreviated names without context: `enrId`, `enrPending`
- Non-descriptive names: `data`, `result`, `temp`, `x`, frequently reused

**Impact:** Reduced code readability, higher cognitive load, harder onboarding.

**Recommendation:** Use descriptive names that convey meaning: `userName` instead of `u`, `courseId` instead of `cid`, `enrollmentPending` instead of `enrPending`.

---

## AP-18: Magic Numbers — LOW

**Severity:** LOW

**Detection signals:**
- Numeric literals used in validation or business logic without named constants
- Comparisons like `len(name) < 2`, `len(title) > 200`, `priority > 5`
- Threshold values: `if faturamento > 10000` without named constant
- Status code numbers in logic: `if status == 200` (instead of `HTTPStatus.OK`)

**Impact:** What does 2 mean? 200? 10000? Magic numbers require tribal knowledge and are error-prone when changed.

**Recommendation:** Define named constants at module level or in a constants/config file: `MIN_NAME_LENGTH = 2`, `HIGH_REVENUE_THRESHOLD = 10000`.

---

## AP-19: Bare Except Clauses — MEDIUM

**Severity:** MEDIUM

**Detection signals:**
- `except:` without exception type specification
- `try: ... except: ...` catching all exceptions including KeyboardInterrupt and SystemExit
- Catching exceptions and returning generic error messages

**Impact:** Hides bugs, makes debugging impossible, catches unintended exceptions.

**Recommendation:** Always specify exception type: `except ValueError:` or `except Exception as e:`. Log the actual error for debugging.

---

## AP-20: Payment Key / Sensitive Data in Logs — HIGH

**Severity:** HIGH

**Detection signals:**
- `console.log()` or `print()` statements containing API keys, tokens, or card numbers
- Log messages with: `config.paymentGatewayKey`, credit card numbers, passwords
- Pattern: `log(..., key, ...)` or `print("chave: " + key)`

**Impact:** Credentials stored in log files, log aggregation systems, or monitoring tools — becoming additional attack vectors.

**Recommendation:** Never log sensitive data. Use log scrubbing or structured logging with explicit field exclusion for secrets.

---

## Summary Table

| ID | Anti-Pattern | Severity |
|----|-------------|----------|
| AP-01 | Hardcoded Credentials | CRITICAL |
| AP-02 | SQL Injection | CRITICAL |
| AP-03 | God Class / God Object | CRITICAL |
| AP-04 | Exposed Secrets in API Responses | CRITICAL |
| AP-05 | Arbitrary Query Execution | CRITICAL |
| AP-06 | Weak Cryptography / Deprecated Hashes | HIGH |
| AP-07 | Business Logic in Routing Layer | HIGH |
| AP-08 | N+1 Query Problem | MEDIUM |
| AP-09 | Duplicated Validation Logic | MEDIUM |
| AP-10 | Missing Input Validation | MEDIUM |
| AP-11 | Global Mutable State | MEDIUM |
| AP-12 | Missing CASCADE on Delete | MEDIUM |
| AP-13 | Deprecated API Usage | MEDIUM |
| AP-14 | Hardcoded Debug Mode | HIGH |
| AP-15 | Callback Hell | MEDIUM |
| AP-16 | Print Statements for Logging | LOW |
| AP-17 | Poor Variable Naming | LOW |
| AP-18 | Magic Numbers | LOW |
| AP-19 | Bare Except Clauses | MEDIUM |
| AP-20 | Payment Key / Sensitive Data in Logs | HIGH |
