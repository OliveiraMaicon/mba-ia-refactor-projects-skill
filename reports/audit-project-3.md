================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.0.0 + SQLAlchemy 3.1.1
Dependencies:  flask-cors, flask-sqlalchemy, marshmallow, python-dotenv, bcrypt
Domain:        Task Manager API (tasks, users, categories, reports)
Architecture:  Parcialmente Organizada — models/, routes/, services/, utils/ existentes mas com lógica de negócio nas rotas
Source files:  13 files analyzed
DB tables:     tasks, users, categories
================================
================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask + SQLAlchemy
Files:   13 analyzed | ~900 lines of code

## Summary
CRITICAL: 3 | HIGH: 2 | MEDIUM: 5 | LOW: 4

## Findings

### [CRITICAL] Hardcoded Credentials (AP-01)
File: app.py:13, services/notification_service.py:9-10
Description: `SECRET_KEY` is hardcoded as `'super-secret-key-123'` in app.py. Email credentials (`email_user = 'taskmanager@gmail.com'`, `email_password = 'senha123'`) are hardcoded in the NotificationService constructor.
Impact: Session tokens forgeable. Email account credentials exposed in version control, allowing anyone to send emails as the application.
Recommendation: Move all credentials to environment variables loaded from config/settings.py.

### [CRITICAL] Weak Cryptography — MD5 Password Hashing (AP-06)
File: models/user.py:29,32
Description: `set_password()` uses `hashlib.md5(pwd.encode()).hexdigest()` for password hashing. `check_password()` compares MD5 hashes directly.
Impact: MD5 is cryptographically broken. Passwords are crackable in seconds using rainbow tables. No salt is used, making identical passwords produce identical hashes.
Recommendation: Replace MD5 with bcrypt. Add `bcrypt` to dependencies. Use `bcrypt.hashpw()` and `bcrypt.checkpw()`.

### [CRITICAL] Exposed Secrets in API Response (AP-04)
File: models/user.py:17-25
Description: `User.to_dict()` includes the `password` field in its output dictionary. This field is returned in user list, user detail, user creation, and login endpoints.
Impact: Password hashes (even hashed) are exposed to every API consumer. Combined with weak MD5 hashing, this is a severe data leak.
Recommendation: Remove `password` from `to_dict()`. Never include sensitive fields in serialization.

### [HIGH] Business Logic in Routes (AP-07)
File: routes/task_routes.py:11-61,85-154,156-223
Description: Task routes contain extensive business logic: manual dict construction (30+ lines in get_tasks), overdue calculation logic (duplicated 4 times), N+1 queries inline, and validation rules.
Impact: Routes are 299 lines. Business logic cannot be unit tested. Overdue logic changes require updating 4+ locations.
Recommendation: Extract to TaskController with service layer. Routes should only delegate to controllers.

### [HIGH] Overdue Logic Duplication (AP-07, AP-09)
File: routes/task_routes.py:30-39,71-80,283-287, routes/user_routes.py:171-181, routes/report_routes.py:33-43
Description: The same overdue check logic (check due_date, compare with utcnow, check status not done/cancelled) is implemented 5 different times across 3 route files.
Impact: Any change to overdue rules requires finding and updating 5 locations. Inconsistent implementations can produce different results.
Recommendation: Use `Task.is_overdue()` method (already exists in model but unused by routes). Routes should call the model method.

### [MEDIUM] N+1 Query Problem (AP-08)
File: routes/task_routes.py:41-57
Description: `get_tasks()` loops over all tasks and executes a separate `User.query.get()` and `Category.query.get()` for each task to get user_name and category_name.
Impact: For 10 tasks, ~21 database queries instead of 1 with joinedload.
Recommendation: Use `Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()` to fetch all related data in one query.

### [MEDIUM] Deprecated API Usage (AP-13)
File: models/task.py:15-16, models/user.py:14, models/category.py:11
Description: `datetime.utcnow` is used as the default value for `created_at` and `updated_at` columns. This is deprecated in Python 3.12+ and will be removed.
Impact: Deprecation warnings on every application start. Future Python versions will break the application.
Recommendation: Replace with `datetime.now(timezone.utc)` or `lambda: datetime.now(timezone.utc)`.

### [MEDIUM] Bare Except Clauses (AP-19)
File: routes/task_routes.py:62,236
Description: Multiple route handlers use `except:` without specifying exception types. This catches KeyboardInterrupt and SystemExit alongside actual application errors.
Impact: Hides real bugs, makes debugging impossible, can prevent intentional shutdown signals.
Recommendation: Use `except Exception as e:` and log the error. Better yet, use centralized error handling.

### [MEDIUM] Unused Imports (AP-17)
File: routes/task_routes.py:7, utils/helpers.py:3-7
Description: `task_routes.py` imports `json, os, sys, time` but never uses all of them. `helpers.py` imports `os, json, sys, math, hashlib` with many unused.
Impact: Minor cognitive overhead and slightly slower imports.
Recommendation: Remove unused imports.

### [MEDIUM] Fake JWT Token (AP-10)
File: routes/user_routes.py:210
Description: Login endpoint returns `'token': 'fake-jwt-token-' + str(user.id)` — a placeholder token that provides no actual authentication.
Impact: While intentional for development, this misleading token implies security where none exists. No actual JWT verification exists on any endpoint.
Recommendation: Either implement real JWT authentication or clearly document that authentication is not implemented.

### [LOW] Magic Numbers (AP-18)
File: routes/task_routes.py:96,99
Description: `len(title) < 3` and `len(title) > 200` use magic numbers without named constants.
Impact: If minimum title length changes from 3 to 5, must be found and changed in every validation block.
Recommendation: Define `MIN_TITLE_LENGTH = 3` and `MAX_TITLE_LENGTH = 200` constants.

### [LOW] Hardcoded Debug Mode (AP-14)
File: app.py:34
Description: `app.run(debug=True)` hardcoded, enabling the Werkzeug debugger in production if deployed as-is.
Impact: Potential RCE through Werkzeug debugger, stack traces exposed to attackers.
Recommendation: Read debug mode from environment variable, default to False.

### [LOW] Redundant Validation Methods (AP-09)
File: models/task.py:38-43,45-48,50-60
Description: Task model has `validate_status()`, `validate_priority()`, and `is_overdue()` methods that are never called by the routes. Routes re-implement the same logic inline.
Impact: Dead code that was probably intended for reuse but never integrated.
Recommendation: Routes should call these model methods instead of duplicating logic.

### [LOW] Print-based Logging (AP-16)
File: routes/task_routes.py:149,153,219,234, routes/user_routes.py:83,89,147
Description: `print()` statements used throughout route handlers for logging instead of a proper logging framework.
Impact: No log levels, no structured logging, no log routing, messages lost in production.
Recommendation: Use Python's `logging` module with appropriate log levels (INFO, WARNING, ERROR).

================================
Total: 14 findings
================================
