# Project Analysis Heuristics

## Language Detection

Scan for telltale files and code patterns to identify the primary language:

| Signal | Language |
|--------|----------|
| `package.json` exists | Node.js/JavaScript |
| `requirements.txt`, `setup.py`, `pyproject.toml`, `Pipfile` | Python |
| `*.py` files with `import` statements (no semicolons, significant indentation) | Python |
| `*.js` files with `require()` or `import ... from` | JavaScript/Node.js |
| `go.mod`, `*.go` files | Go |
| `Cargo.toml`, `*.rs` files | Rust |
| `pom.xml`, `build.gradle`, `*.java` | Java |
| `Gemfile`, `*.rb` | Ruby |
| `composer.json`, `*.php` | PHP |
| `*.ts`, `tsconfig.json` | TypeScript |

## Framework Detection

### Python Frameworks
| Signal | Framework |
|--------|-----------|
| `from flask import` or `flask` in requirements.txt | Flask |
| `from django` or `django` in requirements.txt | Django |
| `from fastapi import` or `fastapi` in requirements.txt | FastAPI |
| Flask + `flask-sqlalchemy` in deps | Flask with SQLAlchemy ORM |
| Flask + raw `sqlite3` usage | Flask with raw SQL |

### Node.js Frameworks
| Signal | Framework |
|--------|-----------|
| `require('express')` or `express` in package.json | Express.js |
| `require('koa')` | Koa |
| `require('fastify')` | Fastify |
| `require('@nestjs/core')` | NestJS |

## Database Detection

| Signal | Database |
|--------|----------|
| `import sqlite3`, `sqlite3` in deps, `.db` file references | SQLite |
| `import psycopg2`, `psycopg2` in deps | PostgreSQL |
| `import pymysql`, `mysql` in deps | MySQL |
| `import pymongo`, `mongodb` in deps | MongoDB |
| `SQLALCHEMY_DATABASE_URI` config variable | SQLAlchemy-supported DB |
| `CREATE TABLE` statements with SQLite types (INTEGER, TEXT, REAL) | SQLite |

## Architecture Mapping

### Monolithic (Antipattern)
- All business logic, DB, and routing in ≤5 files
- Single file with >300 lines handling multiple domains
- No directory structure beyond root files

### Partially Organized
- Some directory separation (models/, routes/) but:
  - Routes contain business logic
  - No service layer
  - Configurations hardcoded in app entry point

### MVC
- `models/` directory: data definitions, DB schemas
- `controllers/` directory: business logic, request handling
- `views/` or `routes/`: HTTP routes defined in separate files
- `config/`: configuration files
- `services/`: reusable business logic
- `middlewares/`: cross-cutting concerns (auth, error handling)

## Domain Inference

Analyze route names, table names, and variable naming to infer application domain:
- `/produtos`, `/pedidos`, `/usuarios` → E-commerce
- `/tasks`, `/users`, `/categories` → Task Manager / Project Management
- `/courses`, `/enrollments`, `/checkout` → LMS (Learning Management System)
- `/api/checkout`, `/payments` → E-commerce / Payment processing

## File Analysis Count

Count source files excluding:
- `node_modules/`, `__pycache__/`, `.git/`
- `*.db`, `*.sqlite`, `*.pyc`
- Package manager files (`package-lock.json`, `Pipfile.lock`)

Count lines of code by summing non-blank, non-comment lines (approximate via `wc -l` filtering).

## Dependencies Listing

From `requirements.txt` or `package.json` dependencies, list the key packages that indicate:
- Web framework (flask, express, django, fastapi)
- Database drivers (sqlite3, psycopg2, pg, mysql2, mongoose)
- Authentication (flask-jwt, jsonwebtoken, bcrypt, passport)
- CORS, validation, serialization (flask-cors, marshmallow, cors, joi, zod)

## DB Table Discovery

- Parse CREATE TABLE statements in code
- Parse SQLAlchemy model class definitions (`__tablename__`)
- Parse raw SQL CREATE TABLE via string search
- Match route/resource names to table names
