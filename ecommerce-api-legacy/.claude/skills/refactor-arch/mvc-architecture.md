# MVC Architecture Guidelines

## Target Architecture

The refactoring target is a clean MVC (Model-View-Controller) architecture with additional layers for configuration, services, and middleware.

## Directory Structure

```
project/
├── config/
│   └── settings.py (or config.js)   # All configuration, env vars
├── src/ (or app root for Python)
│   ├── models/                       # Data definitions
│   │   ├── __init__.py
│   │   ├── user_model.py
│   │   ├── product_model.py
│   │   └── order_model.py
│   ├── controllers/                  # Request handling + orchestration
│   │   ├── __init__.py
│   │   ├── user_controller.py
│   │   ├── product_controller.py
│   │   └── order_controller.py
│   ├── routes/ (or views/)           # HTTP route definitions only
│   │   ├── __init__.py
│   │   ├── user_routes.py
│   │   ├── product_routes.py
│   │   └── order_routes.py
│   ├── services/                     # Business logic (optional but recommended)
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   └── notification_service.py
│   ├── middlewares/                  # Cross-cutting concerns
│   │   ├── __init__.py
│   │   └── error_handler.py
│   └── app.py (or app.js)            # Composition root / entry point
└── requirements.txt (or package.json)
```

## Layer Responsibilities

### Models (`models/`)

**IN:**
- Database schema definitions (ORM models, table definitions)
- Data serialization/deserialization (`to_dict()`, `to_json()`)
- Simple field-level validation (max length, nullability)
- Relationships between entities (foreign keys)
- Database connection configuration

**OUT:**
- Business logic (calculations, workflows)
- HTTP request/response handling
- Route definitions
- Complex validation rules
- Authorization logic

**Python example:**
```python
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price
        }
```

**Node.js example:**
```javascript
class Product {
    constructor(id, name, price) {
        this.id = id;
        this.name = name;
        this.price = price;
    }
    static fromRow(row) {
        return new Product(row.id, row.name, row.price);
    }
}
```

### Controllers (`controllers/`)

**IN:**
- Request parsing and validation
- Calling services and models
- Orchestrating business workflows
- Preparing responses
- Calling multiple services in sequence

**OUT:**
- Direct database queries (delegate to models)
- HTTP route registration (that's routes/views)
- Authentication middleware logic (that's middleware)

**Python example:**
```python
class ProductController:
    def create(self, data):
        errors = self.validate(data)
        if errors:
            return {"error": errors}, 400
        product = ProductService.create_product(data)
        return product.to_dict(), 201
```

### Routes/Views (`routes/` or `views/`)

**IN:**
- HTTP method and path definitions
- URL parameter extraction
- Calling controller methods
- HTTP status codes
- Blueprint/Route registration

**OUT:**
- Business logic
- Database access
- Validation (delegate to controller)

**Python example (Flask Blueprint):**
```python
product_bp = Blueprint('products', __name__)

@product_bp.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    result, status = ProductController().create(data)
    return jsonify(result), status
```

**Node.js example (Express Router):**
```javascript
const router = express.Router();
router.post('/products', (req, res) => {
    const result = productController.create(req.body);
    res.status(result.status).json(result.data);
});
```

### Services (`services/`)

**IN:**
- Complex business logic
- Multi-step workflows
- External API integration
- Calculations and transformations
- Email, notification, payment processing

**OUT:**
- HTTP concerns
- Route definitions
- Direct database schema knowledge (use models)

### Config (`config/`)

**IN:**
- Environment variable loading
- Database connection strings
- API keys (from env vars only)
- Feature flags
- Application constants

**OUT:**
- Hardcoded secrets
- Business logic
- Any credentials in plaintext

### Middlewares (`middlewares/`)

**IN:**
- Error handling (global try/catch)
- Authentication/authorization
- Request logging
- CORS configuration
- Rate limiting

### App Entry Point (`app.py` / `app.js`)

**Responsibilities:**
- Create application instance
- Load configuration
- Register blueprints/routers
- Register middlewares
- Initialize database
- Start server

## Migration Patterns

### From Monolith to MVC

1. **Extract Config**: Move all hardcoded values to `config/settings.py`
2. **Split God Class**: Break the monolithic file into domain-specific model files
3. **Create Controllers**: Extract business logic from routes into controller classes
4. **Create Routes**: Define thin route files that delegate to controllers
5. **Add Middleware**: Centralize error handling, move from try/except per route
6. **Configure Entry Point**: Simplify `app.py` to only wire components together

### From Partially Organized to MVC

1. **Move Logic from Routes to Controllers**: Extract business logic from route files
2. **Create Service Layer**: Extract reusable business logic (notifications, calculations)
3. **Consolidate Validation**: Move duplicated validation into models or dedicated validators
4. **Add Config Module**: Move hardcoded values to config
5. **Centralize Error Handling**: Add error handler middleware

## Security Requirements

- NO credentials in source code — all from environment variables
- NO raw SQL string building — parameterized queries only
- NO secrets in API responses (health, status endpoints)
- NO password fields in `to_dict()` / serialization
- NO debug mode enabled by default
- NO MD5/SHA1 for password hashing — use bcrypt/argon2
- Input validation on ALL endpoints
- Proper error handling without exposing internals
