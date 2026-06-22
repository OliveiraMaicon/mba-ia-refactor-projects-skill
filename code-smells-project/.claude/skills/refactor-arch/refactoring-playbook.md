# Refactoring Playbook

Concrete transformation patterns for each anti-pattern. Each pattern includes: target anti-pattern, before code, after code, and verification steps.

---

## Pattern 1: Extract Hardcoded Credentials to Environment Variables (AP-01, AP-14)

**Target:** Hardcoded Credentials, Hardcoded Debug Mode

### Python — Before
```python
# app.py
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True

# notification_service.py
self.email_password = 'senha123'
```

### Python — After
```python
# config/settings.py
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')

# app.py
from config.settings import SECRET_KEY, DEBUG
app.config["SECRET_KEY"] = SECRET_KEY
app.config["DEBUG"] = DEBUG

# .env.example (committed to git)
SECRET_KEY=change-me-in-production
DEBUG=false
EMAIL_PASSWORD=
```

### Node.js — Before
```javascript
// utils.js
const config = {
    dbPass: "senha_super_secreta_prod_123",
    paymentGatewayKey: "pk_live_1234567890abcdef",
};
```

### Node.js — After
```javascript
// config/index.js
require('dotenv').config();
module.exports = {
    dbUser: process.env.DB_USER || 'default_user',
    dbPass: process.env.DB_PASS || '',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    port: process.env.PORT || 3000,
};

// .env.example
DB_PASS=
PAYMENT_GATEWAY_KEY=
PORT=3000
```

**Verification:** App boots with env vars. `.env` is in `.gitignore`. `.env.example` is committed.

---

## Pattern 2: Replace SQL String Concatenation with Parameterized Queries (AP-02)

**Target:** SQL Injection

### Python — Before
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute(
    "INSERT INTO produtos (nome, preco) VALUES ('" +
    nome + "', " + str(preco) + ")"
)
cursor.execute(
    "SELECT * FROM produtos WHERE nome LIKE '%" + termo + "%'"
)
```

### Python — After
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute(
    "INSERT INTO produtos (nome, preco) VALUES (?, ?)",
    (nome, preco)
)
cursor.execute(
    "SELECT * FROM produtos WHERE nome LIKE ?",
    (f"%{termo}%",)
)
```

### Node.js — Before
```javascript
db.get("SELECT * FROM users WHERE email = '" + email + "'", callback);
```

### Node.js — After
```javascript
db.get("SELECT * FROM users WHERE email = ?", [email], callback);
```

**Verification:** No `+ str(` or `+ '` or `+ "` in SQL string construction. All user input passed via parameter array.

---

## Pattern 3: Split God Class into Domain Modules (AP-03)

**Target:** God Class / God Object

### Python — Before
```
models.py (314 lines)
├── get_todos_produtos()
├── get_produto_por_id()
├── criar_produto()
├── atualizar_produto()
├── deletar_produto()
├── get_todos_usuarios()
├── get_usuario_por_id()
├── login_usuario()
├── criar_usuario()
├── criar_pedido()
├── get_pedidos_usuario()
├── get_todos_pedidos()
├── relatorio_vendas()
├── buscar_produtos()
```

### Python — After
```
models/
├── __init__.py
├── produto_model.py    # Product CRUD functions
├── usuario_model.py    # User CRUD + login
├── pedido_model.py     # Order CRUD + item management
└── relatorio_model.py  # Report queries

controllers/
├── __init__.py
├── produto_controller.py
├── usuario_controller.py
├── pedido_controller.py
└── relatorio_controller.py
```

**Verification:** Each model file < 100 lines. Each handles one domain. No cross-domain imports in models.

---

## Pattern 4: Remove Secrets from API Responses (AP-04)

**Target:** Exposed Secrets in API Responses

### Python — Before
```python
def health_check():
    return jsonify({
        "status": "ok",
        "secret_key": "minha-chave-super-secreta-123",
        "db_path": "loja.db",
    })

class User:
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'password': self.password,  # EXPOSED!
        }
```

### Python — After
```python
def health_check():
    return jsonify({
        "status": "ok",
        "database": "connected",
    })

class User:
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            # password NEVER included
        }
```

**Verification:** Health endpoint returns only status info. User endpoints never return password hash. Grep for `secret_key` in route responses — must be zero.

---

## Pattern 5: Replace Weak Hashing with bcrypt/argon2 (AP-06)

**Target:** Weak Cryptography / Deprecated Hash Functions

### Python — Before
```python
import hashlib

def set_password(self, pwd):
    self.password = hashlib.md5(pwd.encode()).hexdigest()

def check_password(self, pwd):
    return self.password == hashlib.md5(pwd.encode()).hexdigest()
```

### Python — After
```python
import bcrypt

def set_password(self, pwd):
    salt = bcrypt.gensalt()
    self.password = bcrypt.hashpw(pwd.encode('utf-8'), salt).decode('utf-8')

def check_password(self, pwd):
    return bcrypt.checkpw(pwd.encode('utf-8'), self.password.encode('utf-8'))
```

### Node.js — Before
```javascript
function badCrypto(pwd) {
    let hash = "";
    for(let i = 0; i < 10000; i++) {
        hash += Buffer.from(pwd).toString('base64').substring(0, 2);
    }
    return hash.substring(0, 10);
}
```

### Node.js — After
```javascript
const bcrypt = require('bcrypt');
const saltRounds = 10;

async function hashPassword(password) {
    return bcrypt.hash(password, saltRounds);
}

async function checkPassword(password, hash) {
    return bcrypt.compare(password, hash);
}
```

**Verification:** No `md5`, `sha1`, or custom loop-based hashing. Add `bcrypt` to dependencies.

---

## Pattern 6: Extract Business Logic from Routes to Controllers (AP-07)

**Target:** Business Logic in Routing Layer

### Python — Before
```python
@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    result = []
    for t in tasks:
        data = {}
        # 30 lines of building task_data...
        # overdue logic...
        # N+1 queries for user/category...
        result.append(data)
    return jsonify(result), 200
```

### Python — After
```python
# controllers/task_controller.py
class TaskController:
    def get_all_tasks(self):
        tasks = TaskService.get_all_with_details()  # single query with JOINs
        return [t.to_dict() for t in tasks], 200

# routes/task_routes.py
@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    result, status = TaskController().get_all_tasks()
    return jsonify(result), status
```

### Node.js — Before (Express)
```javascript
app.get('/api/admin/financial-report', (req, res) => {
    // 50 lines of nested callbacks, queries, calculations...
});
```

### Node.js — After (Express)
```javascript
// controllers/reportController.js
class ReportController {
    async getFinancialReport() { /* business logic */ }
}

// routes/reportRoutes.js
router.get('/api/admin/financial-report', async (req, res) => {
    const report = await reportController.getFinancialReport();
    res.json(report);
});
```

**Verification:** Route handlers are < 10 lines. Business logic lives in controllers/services.

---

## Pattern 7: Fix N+1 Queries with JOINs or Batch Loading (AP-08)

**Target:** N+1 Query Problem

### Python — Before
```python
pedidos = cursor.execute("SELECT * FROM pedidos").fetchall()
for pedido in pedidos:
    itens = cursor.execute(
        "SELECT * FROM itens_pedido WHERE pedido_id = " + str(pedido["id"])
    ).fetchall()
    for item in itens:
        prod = cursor.execute(
            "SELECT nome FROM produtos WHERE id = " + str(item["produto_id"])
        ).fetchone()
```

### Python — After
```python
# Fetch everything with joins
cursor.execute("""
    SELECT p.*, ip.*, prod.nome as produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido ip ON p.id = ip.pedido_id
    LEFT JOIN produtos prod ON ip.produto_id = prod.id
    ORDER BY p.id
""")
# Then group in application code
pedidos = {}
for row in rows:
    if row["id"] not in pedidos:
        pedidos[row["id"]] = {"id": row["id"], "itens": []}
    pedidos[row["id"]]["itens"].append(...)
```

### ORM — Before (Flask-SQLAlchemy N+1)
```python
tasks = Task.query.all()
for t in tasks:
    user = User.query.get(t.user_id)  # N queries!
    category = Category.query.get(t.category_id)  # N queries!
```

### ORM — After
```python
from sqlalchemy.orm import joinedload
tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
```

**Verification:** No queries inside loops. Related data fetched via JOIN or eager loading.

---

## Pattern 8: Centralize Error Handling with Middleware (AP-07, AP-19)

**Target:** Repeated try/except blocks, bare except clauses

### Python Flask — Before
```python
@bp.route('/x', methods=['GET'])
def handle_x():
    try:
        # business logic
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@bp.route('/y', methods=['POST'])
def handle_y():
    try:
        # business logic
        return jsonify(result), 201
    except:
        return jsonify({"erro": "Erro"}), 500
```

### Python Flask — After
```python
# middlewares/error_handler.py
from flask import jsonify
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": str(error.description)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.exception("Internal server error")
        return jsonify({"error": "Internal server error"}), 500

# app.py
from middlewares.error_handler import register_error_handlers
register_error_handlers(app)

# routes — clean, no try/except
@bp.route('/x', methods=['GET'])
def handle_x():
    result = controller.do_thing()
    return jsonify(result), 200
```

### Node.js Express — Before
```javascript
app.get('/api/x', (req, res) => {
    try { /* ... */ } catch(e) { res.status(500).send("error"); }
});
```

### Node.js Express — After
```javascript
// middlewares/errorHandler.js
function errorHandler(err, req, res, next) {
    console.error(err.stack);
    res.status(err.status || 500).json({ error: 'Internal server error' });
}

// app.js
app.use(errorHandler);

// routes — wrap with async handler or use express-async-errors
```

**Verification:** Route files have zero try/except blocks. Single error handler registered in app entry point.

---

## Pattern 9: Extract Duplicated Validation to Shared Module (AP-09)

**Target:** Duplicated Validation Logic

### Python — Before
```python
# create
if not data: return error
if "nome" not in data: return error
if "preco" not in data: return error
if preco < 0: return error
if len(nome) < 2: return error

# update — same validations repeated
if not data: return error
if "nome" not in data: return error
if "preco" not in data: return error
if preco < 0: return error
if len(nome) < 2: return error
```

### Python — After
```python
# validators/product_validator.py
class ProductValidator:
    @staticmethod
    def validate(data):
        errors = []
        if not data: errors.append("Dados inválidos")
        if "nome" not in data: errors.append("Nome é obrigatório")
        if "preco" not in data: errors.append("Preço é obrigatório")
        if errors: return errors
        if data.get("preco", 0) < 0: errors.append("Preço não pode ser negativo")
        if len(data.get("nome", "")) < 2: errors.append("Nome muito curto")
        return errors

# controller
errors = ProductValidator.validate(data)
if errors: return {"erro": errors[0]}, 400
```

### Node.js — Before
```javascript
// Validation scattered in routes
if (!req.body.usr || !req.body.eml || !req.body.c_id) return res.status(400).send("Bad Request");
```

### Node.js — After
```javascript
// validators/checkoutValidator.js
const Joi = require('joi');
const checkoutSchema = Joi.object({
    usr: Joi.string().required(),
    eml: Joi.string().email().required(),
    pwd: Joi.string().min(4).required(),
    c_id: Joi.number().integer().required(),
    card: Joi.string().creditCard().required(),
});

// middleware
function validate(schema) {
    return (req, res, next) => {
        const { error } = schema.validate(req.body);
        if (error) return res.status(400).json({ error: error.details[0].message });
        next();
    };
}
router.post('/checkout', validate(checkoutSchema), handler);
```

**Verification:** Same validation rule appears only once in codebase. Grep confirms no duplicated if/else validation chains.

---

## Pattern 10: Replace Deprecated utcnow() with timezone-aware equivalent (AP-13)

**Target:** Deprecated API Usage

### Python — Before
```python
from datetime import datetime
created_at = db.Column(db.DateTime, default=datetime.utcnow)
due_date = datetime.utcnow() + timedelta(days=5)
```

### Python — After
```python
from datetime import datetime, timezone
created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
due_date = datetime.now(timezone.utc) + timedelta(days=5)
```

**Verification:** Zero occurrences of `utcnow()` or `utcfromtimestamp()` in codebase.

---

## Pattern 11: Add CASCADE Delete for Referential Integrity (AP-12)

**Target:** Missing CASCADE on Delete

### SQLite — Before
```sql
CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER);
CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL);
-- Deleting user leaves orphan enrollments and payments
```

### SQLite — After
```sql
CREATE TABLE enrollments (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    course_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TABLE payments (
    id INTEGER PRIMARY KEY,
    enrollment_id INTEGER,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE
);
```

**Verification:** Deleting a parent record also deletes children. No orphan records after delete.

---

## Pattern 12: Convert Callback Hell to Async/Await (AP-15)

**Target:** Callback Hell (Node.js)

### Node.js — Before
```javascript
db.get("SELECT * FROM courses WHERE id = ?", [cid], (err, course) => {
    db.get("SELECT id FROM users WHERE email = ?", [e], (err, user) => {
        db.run("INSERT INTO enrollments ...", [...], function(err) {
            db.run("INSERT INTO payments ...", [...], function(err) {
                db.run("INSERT INTO audit_logs ...", [...], (err) => {
                    res.json({ msg: "Sucesso" });
                });
            });
        });
    });
});
```

### Node.js — After
```javascript
const util = require('util');
// Or use better-sqlite3, sqlite3 with async wrapper, or sequelize

async function handleCheckout(req, res, next) {
    try {
        const course = await dbGet("SELECT * FROM courses WHERE id = ?", [cid]);
        if (!course) return res.status(404).json({ error: "Course not found" });

        let user = await dbGet("SELECT id FROM users WHERE email = ?", [e]);
        if (!user) {
            const result = await dbRun("INSERT INTO users ...", [u, e, hash]);
            user = { id: result.lastID };
        }

        const enrResult = await dbRun("INSERT INTO enrollments ...", [user.id, cid]);
        await dbRun("INSERT INTO payments ...", [enrResult.lastID, course.price, status]);
        await dbRun("INSERT INTO audit_logs ...", [`Checkout ${cid}`]);

        res.json({ msg: "Sucesso", enrollment_id: enrResult.lastID });
    } catch (err) {
        next(err);
    }
}
```

**Verification:** No nested callback pyramids > 2 levels. Linear code flow with async/await.

---

## Validation Checklist (Post-Refactoring)

After refactoring, verify:

1. **Boot test**: Application starts without errors
2. **Endpoint test**: All original endpoints return expected responses
3. **Zero anti-patterns**: Re-run Phase 2 audit — should find 0 findings
4. **Structure check**: Directory structure matches MVC target
5. **Config check**: No hardcoded secrets in source code
6. **Security check**: No raw SQL concatenation, no secrets in responses
7. **Error handling**: Centralized error handler registered

Run the application and hit each endpoint from the original API to confirm functionality.
