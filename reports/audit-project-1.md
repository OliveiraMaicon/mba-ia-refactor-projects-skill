================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.1.1
Dependencies:  flask-cors, python-dotenv
Domain:        E-commerce API (produtos, pedidos, usuarios)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 5 | HIGH: 3 | MEDIUM: 6 | LOW: 4

## Findings

### [CRITICAL] Arbitrary SQL Execution Endpoint (AP-05)
File: app.py:59-78
Description: The /admin/query endpoint accepts raw SQL and executes it directly, allowing anyone to run any query including DROP TABLE, DELETE, or SELECT * to exfiltrate data.
Impact: Complete database takeover — any attacker can read, modify, or destroy all data.
Recommendation: Remove the endpoint entirely. If dynamic queries are needed, use a query builder with whitelisted operations.

### [CRITICAL] SQL Injection — String Concatenation in Queries (AP-02)
File: models.py:28,47-49,57-60,92,109-110,126-128,140,149-151,155-166,174,188-192,220-224,279-281,291-296
Description: Every SQL query in models.py uses string concatenation to build queries (e.g., `"SELECT * FROM produtos WHERE id = " + str(id)`). There are over 15 vulnerable queries.
Impact: SQL injection can expose all customer data, modify orders, or destroy the database.
Recommendation: Replace all string-concatenated queries with parameterized queries using `?` placeholders.

### [CRITICAL] Hardcoded Credentials (AP-01)
File: app.py:7
Description: SECRET_KEY hardcoded as 'minha-chave-super-secreta-123' in the application source code.
Impact: Session tokens can be forged because the secret key is known. Key cannot be rotated without code changes.
Recommendation: Move to environment variable via `os.getenv('SECRET_KEY')`.

### [CRITICAL] Exposed Secrets in API Response (AP-04)
File: controllers.py:284-294
Description: The /health endpoint (`health_check()`) returns `secret_key`, `db_path`, `debug` flag, and `ambiente` in the JSON response.
Impact: Anyone hitting the health endpoint can discover the secret key, database path, and debug mode — aiding targeted attacks.
Recommendation: Remove all sensitive fields from the health response. Return only `status` and `database`.

### [CRITICAL] God Class / God Object (AP-03)
File: models.py:1-314
Description: Single file contains all business logic, SQL queries, validation, and response formatting for 4 different domains (products, users, orders, reports).
Impact: Impossible to test in isolation. Any change affects all domains. 314 lines in one file with no separation of concerns.
Recommendation: Split into domain-specific modules — product_model.py, user_model.py, order_model.py, report_model.py.

### [HIGH] Hardcoded Debug Mode (AP-14)
File: app.py:8,88
Description: `DEBUG = True` is hardcoded in both the config and the `app.run()` call.
Impact: Detailed error pages and the Werkzeug debugger are exposed in production, potentially leaking stack traces and allowing code execution.
Recommendation: Read debug mode from environment variable, defaulting to False.

### [HIGH] Business Logic in Controllers (AP-07)
File: controllers.py:24-62,64-97,188-220
Description: Controllers contain extensive validation logic (40+ lines in `criar_produto()`), notification logic (email/SMS/push simulated in `criar_pedido()`), and status update side effects.
Impact: Business rules duplicated between create and update, impossible to unit test in isolation.
Recommendation: Extract validation to a Validator class and business logic to a Service layer.

### [HIGH] No Error Handling Middleware (AP-07)
File: controllers.py (all functions)
Description: Every single controller function has a try/except block returning `{"erro": str(e)}, 500`. Repeated ~20 times.
Impact: Error handling duplicated across every endpoint, no centralized logging, inconsistent error format.
Recommendation: Create a centralized Flask error handler with `@app.errorhandler` decorators.

### [MEDIUM] N+1 Query Problem (AP-08)
File: models.py:171-201,203-233
Description: `get_pedidos_usuario()` and `get_todos_pedidos()` loop over pedidos, then for each execute nested queries for itens_pedido, then for each item execute another query for product name.
Impact: Instead of 1-2 queries, hundreds are executed. For 10 orders with 5 items each: ~60 queries.
Recommendation: Use JOINs to fetch order items with product names in a single query per order.

### [MEDIUM] Duplicated Validation Logic (AP-09)
File: controllers.py:28-53,74-90
Description: The same validation rules (nome required, preco required, estoque required, preco >= 0) appear identically in both `criar_produto()` and `atualizar_produto()`.
Impact: Changes to validation require updates in multiple places, risking inconsistencies.
Recommendation: Extract validation to a shared `ProductValidator` class.

### [MEDIUM] Missing Input Validation (AP-10)
File: controllers.py:146-165,167-186
Description: The `criar_usuario()` function accepts any email format and `login()` compares passwords in plaintext without hashing or rate limiting.
Impact: Invalid data stored in database, passwords stored in plaintext, brute-force login possible.
Recommendation: Add email format validation, hash passwords with bcrypt, and add rate limiting on login.

### [MEDIUM] Global Mutable State (AP-11)
File: database.py:4-5
Description: `db_connection = None` is modified via `global db_connection` inside `get_db()`, creating a shared mutable singleton.
Impact: Not thread-safe. Multiple concurrent requests share the same connection. `check_same_thread=False` is a workaround masking the real issue.
Recommendation: Use Flask's `g` object or a connection pool with proper request-scoped lifecycle.

### [MEDIUM] Deprecated API Usage (AP-13)
File: database.py:54
Description: Uses `sqlite3.connect(db, check_same_thread=False)` — the `check_same_thread=False` parameter is a deprecated workaround that masks thread-safety issues in web apps.
Impact: Possible data corruption under concurrent access.
Recommendation: Use Flask-SQLAlchemy which manages connections properly, or use a WSGI-compatible connection pool.

### [MEDIUM] Bare Except Clauses (AP-19)
File: controllers.py (all functions)
Description: All controller functions use generic `except Exception as e:` without logging the original error details beyond `print()`.
Impact: Error investigation requires checking server console output. Errors silently swallowed in some paths.
Recommendation: Use centralized error handling with proper logging.

### [LOW] Print Statements for Logging (AP-16)
File: controllers.py:8,11,57,61,106,161,179,182,208-210,248-250
Description: `print()` statements are used throughout controllers for logging, including sensitive data like user emails and order details.
Impact: No log level control, no structured logging, PII exposed in console output.
Recommendation: Replace with Python's `logging` module with appropriate log levels.

### [LOW] Magic Numbers (AP-18)
File: controllers.py:47,49,52
Description: Hardcoded values like `2` (minimum name length), `200` (maximum name length), and category list defined inline.
Impact: What does "2" mean? If the minimum changes, it must be found and changed in every controller function.
Recommendation: Define constants: `MIN_NAME_LENGTH = 2`, `MAX_NAME_LENGTH = 200`.

### [LOW] Unused Import (AP-17)
File: models.py:2
Description: `import sqlite3` at the top of models.py is unused — all DB access goes through `database.get_db()`.
Impact: Minor — unused imports increase cognitive load and slightly slow import times.
Recommendation: Remove the unused import.

### [LOW] Sensitive Info in Health Endpoint (AP-17)
File: controllers.py:284-294
Description: The health check endpoint returns `versao: "1.0.0"`, `ambiente: "producao"`, `debug: True`, and `secret_key` which leak internal configuration.
Impact: Attackers can fingerprint the application and discover sensitive config.
Recommendation: Remove all non-essential fields from health endpoint responses.

================================
Total: 18 findings
================================
