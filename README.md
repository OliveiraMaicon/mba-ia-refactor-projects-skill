# Skill de Auditoria e Refatoração Arquitetural (`refactor-arch`)

Skill para Claude Code que automatiza a análise, auditoria e refatoração de projetos legados para o padrão MVC, independente da tecnologia.

---

## A) Análise Manual

Análise detalhada dos 3 projetos entregues antes da criação da skill.

### Projeto 1: code-smells-project (Python/Flask — API de E-commerce)

**Arquitetura:** Monolítica — 4 arquivos, ~800 linhas, sem separação de camadas.

| # | Problema | Severidade | Arquivo:Linha | Justificativa |
|---|----------|-----------|---------------|---------------|
| 1 | Hardcoded Credentials | **CRITICAL** | `app.py:7` | SECRET_KEY exposta no código-fonte permite forjar sessões. Qualquer um com acesso ao repo pode decodificar tokens. |
| 2 | SQL Injection | **CRITICAL** | `models.py:28,47-49,57-60,92,109-110,126-128,140,149-151,155-166,174,188-192,220-224,279-281,291-296` | 15+ queries com concatenação de string. Um ataque de SQL injection pode expor todos os dados de clientes e pedidos. |
| 3 | Arbitrary SQL Execution | **CRITICAL** | `app.py:59-78` | Endpoint `/admin/query` permite executar SQL arbitrário sem autenticação. DROP TABLE, DELETE, exfiltração total. |
| 4 | Exposed Secrets em API Response | **CRITICAL** | `controllers.py:284-294` | `/health` retorna `secret_key`, `db_path`, `debug` no JSON. Scanner automatizado descobre as credenciais. |
| 5 | God Class | **CRITICAL** | `models.py:1-314` | Arquivo único com toda lógica de 4 domínios (produtos, usuários, pedidos, relatórios). Impossível testar isoladamente. |
| 6 | Debug Mode Hardcoded | **HIGH** | `app.py:8,88` | `DEBUG=True` expõe stack traces e Werkzeug debugger em produção. Risco de RCE. |
| 7 | Business Logic nos Controllers | **HIGH** | `controllers.py:24-62,188-220` | Validação de 40+ linhas e notificações dentro dos controllers. Sem teste unitário possível. |
| 8 | N+1 Queries | **MEDIUM** | `models.py:171-201` | Loop sobre pedidos executa queries aninhadas para itens e nomes de produtos. ~60 queries em vez de 2. |
| 9 | Validação Duplicada | **MEDIUM** | `controllers.py:28-53,74-90` | Mesmas regras em `criar_produto()` e `atualizar_produto()`. Mudança requer update em 2 lugares. |
| 10 | Global Mutable State | **MEDIUM** | `database.py:4-5` | `db_connection` global mutável com `check_same_thread=False`. Não é thread-safe. |
| 11 | Print Statements | **LOW** | `controllers.py:8,57,61,208-210` | Print usado para logging, inclusive dados sensíveis como emails. Sem log level ou structured logging. |
| 12 | Magic Numbers | **LOW** | `controllers.py:47,49` | `2` (min nome) e `200` (max nome) sem constantes nomeadas. |

### Projeto 2: ecommerce-api-legacy (Node.js/Express — LMS API)

**Arquitetura:** Monolítica — God Class `AppManager.js` contém DB, rotas, checkout, relatórios e deleção.

| # | Problema | Severidade | Arquivo:Linha | Justificativa |
|---|----------|-----------|---------------|---------------|
| 1 | Hardcoded Secrets | **CRITICAL** | `src/utils.js:1-7` | Credenciais de produção expostas: `dbPass`, `paymentGatewayKey`, `smtpUser`. Chave do gateway de pagamento no código. |
| 2 | Weak Cryptography (badCrypto) | **CRITICAL** | `src/utils.js:17-23` | Função "hash" customizada que faz loop com base64 e trunca para 10 chars. Não é hashing real — é encoding reversível. |
| 3 | God Class | **CRITICAL** | `src/AppManager.js:4-139` | Classe única com DB init, schema, seeds, rotas, checkout, financial report e user delete. 139 linhas monolíticas. |
| 4 | Payment Key in Logs | **HIGH** | `src/AppManager.js:45` | `console.log` imprime a chave real do gateway de pagamento nos logs. Exposta em sistemas de log aggregation. |
| 5 | No Password Validation | **HIGH** | `src/AppManager.js:28-36` | Senha opcional no checkout com fallback `"123456"`. Usuários criados com senhas padrão ou vazias. |
| 6 | Callback Hell | **MEDIUM** | `src/AppManager.js:37-77` | 5 níveis de callbacks aninhados no checkout. Debugging e error handling praticamente impossíveis. |
| 7 | N+1 Queries | **MEDIUM** | `src/AppManager.js:80-128` | Financial report: loop courses → loop enrollments → query user → query payment. Explosão combinatória de queries. |
| 8 | Missing CASCADE Delete | **MEDIUM** | `src/AppManager.js:131-136` | DELETE user sem remover enrollments e payments. Resposta admite: "ficaram sujos no banco". |
| 9 | Global Mutable State | **MEDIUM** | `src/utils.js:9-10` | `globalCache` e `totalRevenue` globais mutáveis. Memory leak e data leak entre requests. |
| 10 | Poor Variable Naming | **LOW** | `src/AppManager.js:29-33` | `u`, `e`, `p`, `cid`, `cc` — variáveis de 1-2 letras ilegíveis sem contexto. |
| 11 | Inconsistent Error Responses | **LOW** | `src/AppManager.js:35,38` | Mix de `res.send("Bad Request")` (texto) e `res.send("Erro DB")` (texto). Cliente não consegue parse uniforme. |

### Projeto 3: task-manager-api (Python/Flask — Task Manager API)

**Arquitetura:** Parcialmente organizada — possui `models/`, `routes/`, `services/`, `utils/` mas com lógica de negócio nas rotas.

| # | Problema | Severidade | Arquivo:Linha | Justificativa |
|---|----------|-----------|---------------|---------------|
| 1 | Hardcoded Credentials | **CRITICAL** | `app.py:13`, `services/notification_service.py:9-10` | SECRET_KEY e credenciais de email hardcoded. Conta de email comprometida no repo. |
| 2 | MD5 Password Hashing | **CRITICAL** | `models/user.py:29-32` | `hashlib.md5()` para senhas sem salt. MD5 está quebrado criptograficamente — rainbow tables crackeiam em segundos. |
| 3 | Password Exposed in API | **CRITICAL** | `models/user.py:17-25` | `to_dict()` inclui campo `password`. Hash (mesmo fraco) exposto em listagem de usuários, criação e login. |
| 4 | Business Logic in Routes | **HIGH** | `routes/task_routes.py:11-61,85-154` | Rotas com 299 linhas contendo construção manual de dicts, N+1 queries, e validação inline. |
| 5 | Overdue Logic Duplication | **HIGH** | `routes/task_routes.py`, `user_routes.py`, `report_routes.py` | Mesma lógica overdue implementada 5 vezes em 3 arquivos. Model já tem `is_overdue()` mas não é usado. |
| 6 | N+1 Query | **MEDIUM** | `routes/task_routes.py:41-57` | Loop sobre tasks executa `User.query.get()` e `Category.query.get()` por task. 21 queries em vez de 1. |
| 7 | Deprecated `utcnow()` | **MEDIUM** | `models/task.py:15-16`, `user.py:14`, `category.py:11` | `datetime.utcnow()` deprecado no Python 3.12+. Vai quebrar em versões futuras. |
| 8 | Bare Except Clauses | **MEDIUM** | `routes/task_routes.py:62,236` | `except:` sem tipo de exceção captura KeyboardInterrupt e SystemExit junto com erros reais. |
| 9 | Unused Imports | **LOW** | `routes/task_routes.py:7`, `utils/helpers.py:3-7` | `json, os, sys, time, math, hashlib` importados e não usados. |
| 10 | Magic Numbers | **LOW** | `routes/task_routes.py:96,99` | `3` e `200` como limites de título sem constantes nomeadas. |

---

## B) Construção da Skill

### Decisões de Design

**Estrutura do SKILL.md:**
O SKILL.md foi projetado com 3 fases sequenciais bem definidas que espelham o ciclo completo de auditoria arquitetural: análise → auditoria → refatoração. Cada fase tem objetivos, passos e formato de saída claramente especificados.

**Arquivos de Referência (5 arquivos):**

| Arquivo | Conteúdo | Por que |
|---------|----------|---------|
| `project-analysis.md` | Heurísticas para detectar linguagem, framework, banco, arquitetura e domínio | Essencial para a Fase 1 — fornece os sinais concretos (arquivos, imports, patterns) que permitem identificação agnóstica de stack |
| `anti-patterns-catalog.md` | 20 anti-patterns com sinais de detecção, severidade, impacto e recomendação | Coração da Fase 2 — catálogo completo que a skill cruza contra o código. Cada anti-pattern tem sinais acionáveis (não apenas "código ruim" mas "query SQL dentro de string concatenation") |
| `audit-report-template.md` | Formato exato do relatório com regras de ordenação e formatação | Garante consistência nos 3 projetos — mesmo formato, mesma ordenação CRITICAL→LOW, mesmos campos obrigatórios |
| `mvc-architecture.md` | Regras de arquitetura MVC alvo, responsabilidades de cada camada, estrutura de diretórios | Guia para a Fase 3 — define exatamente onde cada tipo de código deve ficar (models só dados, routes só HTTP, controllers orquestram) |
| `refactoring-playbook.md` | 12 padrões de transformação com código antes/depois em Python e Node.js | Execute da Fase 3 — cada anti-pattern do catálogo tem uma transformação concreta com exemplos reais de código. Cobre ambas as stacks |

### Anti-Patterns Incluídos (20 no total)

Distribuição de severidade: 5 CRITICAL, 4 HIGH, 8 MEDIUM, 3 LOW

| ID | Anti-Pattern | Severidade |
|----|-------------|-----------|
| AP-01 | Hardcoded Credentials | CRITICAL |
| AP-02 | SQL Injection (String Concatenation) | CRITICAL |
| AP-03 | God Class / God Object | CRITICAL |
| AP-04 | Exposed Secrets in API Responses | CRITICAL |
| AP-05 | Arbitrary Query Execution Endpoint | CRITICAL |
| AP-06 | Weak Cryptography / Deprecated Hashes | HIGH |
| AP-07 | Business Logic in Routing Layer | HIGH |
| AP-08 | N+1 Query Problem | MEDIUM |
| AP-09 | Duplicated Validation Logic | MEDIUM |
| AP-10 | Missing Input Validation | MEDIUM |
| AP-11 | Global Mutable State | MEDIUM |
| AP-12 | Missing CASCADE on Delete | MEDIUM |
| AP-13 | Deprecated API Usage | MEDIUM |
| AP-14 | Hardcoded Debug Mode | HIGH |
| AP-15 | Callback Hell (Node.js) | MEDIUM |
| AP-16 | Print Statements for Logging | LOW |
| AP-17 | Poor Variable Naming | LOW |
| AP-18 | Magic Numbers | LOW |
| AP-19 | Bare Except Clauses | MEDIUM |
| AP-20 | Payment Key / Sensitive Data in Logs | HIGH |

**Critérios de seleção:** Os anti-patterns foram selecionados com base nos problemas encontrados na análise manual dos 3 projetos, garantindo cobertura de:
- Segurança (AP-01, AP-02, AP-04, AP-05, AP-06, AP-20)
- Arquitetura (AP-03, AP-07, AP-14, AP-15)
- Performance (AP-08)
- Manutenibilidade (AP-09, AP-10, AP-11, AP-12, AP-19)
- Qualidade de código (AP-16, AP-17, AP-18)
- Compatibilidade futura (AP-13 — APIs deprecated)

### Como a Skill é Agnóstica de Tecnologia

1. **Heurísticas de detecção multilinguagem:** O `project-analysis.md` cobre Python, Node.js, Go, Rust, Java, Ruby e PHP — com sinais específicos para cada stack
2. **Exemplos dual-stack:** O `refactoring-playbook.md` fornece exemplos antes/depois tanto em Python quanto em Node.js para cada padrão
3. **Linguagem neutra no SKILL.md:** As instruções principais não mencionam tecnologias específicas — delegam ao agente a adaptação conforme a stack detectada
4. **Testado em 3 projetos com stacks diferentes:** Python/Flask monolítico, Node.js/Express monolítico, e Python/Flask parcialmente organizado — provando que a skill funciona em contextos variados

### Desafios Encontrados

1. **Precisão de detecção:** Como fazer a skill encontrar problemas reais sem falsos positivos. Solução: sinais de detecção baseados em padrões de código concretos (ex: `"SELECT * FROM x WHERE id = " + str(id)` vs "possível SQL injection")
2. **Adaptação a projetos parcialmente organizados:** O task-manager-api já tinha models/routes/services — a skill precisava identificar que o problema não era falta de estrutura, mas lógica no lugar errado (rotas com 300 linhas)
3. **Transições de dependências:** A refatoração do Node.js exigiu trocar de SQLite3 callback-based para async/await com bcrypt — mudanças que vão além de mover arquivos
4. **Timezone-aware datetimes:** A substituição de `utcnow()` por `datetime.now(timezone.utc)` causou incompatibilidade com dados seedados com datetime naive — exigiu adaptação no modelo

---

## C) Resultados

### Resumo dos Relatórios de Auditoria

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---------|----------|------|--------|-----|-------|
| code-smells-project (Python/Flask) | 5 | 3 | 6 | 4 | **18** |
| ecommerce-api-legacy (Node.js/Express) | 3 | 3 | 5 | 3 | **14** |
| task-manager-api (Python/Flask) | 3 | 2 | 5 | 4 | **14** |

### Comparação Antes/Depois

#### code-smells-project

**Antes:**
```
code-smells-project/
├── app.py          (88 linhas — entry point + rotas + admin SQL injection)
├── controllers.py  (292 linhas — lógica de negócio + validação + notificações)
├── models.py       (314 linhas — God Class com 4 domínios + SQL Injection)
├── database.py     (86 linhas — global state + schema + seeds)
└── requirements.txt
```

**Depois:**
```
code-smells-project/
├── config/
│   └── settings.py           # Config via env vars
├── models/
│   ├── product_model.py      # Domínio produto — queries parametrizadas
│   ├── user_model.py         # Domínio usuário
│   ├── order_model.py        # Domínio pedido — JOINs em vez de N+1
│   └── report_model.py       # Relatórios — constantes nomeadas
├── controllers/
│   ├── product_controller.py # Validação consolidada no controller
│   ├── user_controller.py
│   ├── order_controller.py
│   └── report_controller.py  # Health sem secrets
├── routes/
│   ├── product_routes.py     # Rotas finas (< 20 linhas)
│   ├── user_routes.py
│   ├── order_routes.py
│   └── report_routes.py
├── middlewares/
│   └── error_handler.py      # Tratamento centralizado
├── app.py                    # Composition root (38 linhas)
├── database.py               # Factory sem global state
├── .env.example
├── .gitignore
└── requirements.txt
```

#### ecommerce-api-legacy

**Antes:**
```
ecommerce-api-legacy/
├── src/
│   ├── app.js          (14 linhas — cria AppManager)
│   ├── AppManager.js   (139 linhas — God Class)
│   └── utils.js        (25 linhas — secrets + bad crypto + globals)
├── api.http
└── package.json
```

**Depois:**
```
ecommerce-api-legacy/
├── src/
│   ├── config/
│   │   └── index.js           # Config via env vars
│   ├── models/
│   │   ├── userModel.js       # bcrypt hashing
│   │   ├── courseModel.js
│   │   ├── enrollmentModel.js
│   │   └── paymentModel.js    # + audit logging
│   ├── controllers/
│   │   ├── checkoutController.js  # async/await, sem callback hell
│   │   ├── reportController.js    # JOINs em vez de callbacks aninhados
│   │   └── userController.js      # CASCADE delete
│   ├── routes/
│   │   ├── checkoutRoutes.js
│   │   ├── reportRoutes.js
│   │   └── userRoutes.js
│   ├── middlewares/
│   │   └── errorHandler.js
│   ├── database.js            # Promisified SQLite
│   └── app.js                 # Composition root
├── .env.example
├── .gitignore
└── package.json
```

#### task-manager-api

**Antes:**
```
task-manager-api/
├── app.py          (34 linhas — secret key hardcoded)
├── database.py     (3 linhas — SQLAlchemy init)
├── seed.py
├── models/
│   ├── task.py     (utcnow deprecado)
│   ├── user.py     (MD5 hashing + password no to_dict)
│   └── category.py (utcnow deprecado)
├── routes/
│   ├── task_routes.py    (299 linhas — lógica de negócio)
│   ├── user_routes.py    (211 linhas — lógica de negócio)
│   └── report_routes.py  (223 linhas — lógica de negócio)
├── services/
│   └── notification_service.py (creds hardcoded)
└── utils/
    └── helpers.py
```

**Depois:**
```
task-manager-api/
├── config/
│   └── settings.py           # Config via env vars
├── controllers/              # NOVA CAMADA
│   ├── task_controller.py    # joinedload + is_overdue()
│   ├── user_controller.py    # bcrypt + sem password no output
│   └── report_controller.py  # timezone-aware datetimes
├── models/
│   ├── task.py     (timezone.utc + is_overdue() funcional)
│   ├── user.py     (bcrypt hashing + to_dict sem password)
│   └── category.py (timezone.utc)
├── routes/
│   ├── task_routes.py    # Rotas finas (~40 linhas)
│   ├── user_routes.py    # Rotas finas (~50 linhas)
│   └── report_routes.py  # Rotas finas (~40 linhas)
├── services/
│   └── notification_service.py (creds via env vars)
├── middlewares/
│   └── error_handler.py      # Centralizado
├── app.py                    # Composition root
├── .env.example
├── .gitignore
└── requirements.txt
```

### Checklist de Validação

#### Projeto 1 — code-smells-project

**Fase 1 — Análise**
- [x] Linguagem detectada: Python
- [x] Framework detectado: Flask 3.1.1
- [x] Domínio: E-commerce API
- [x] Arquivos analisados: 4

**Fase 2 — Auditoria**
- [x] Relatório segue template
- [x] Cada finding tem arquivo:linha exatos
- [x] Findings ordenados CRITICAL → LOW
- [x] 18 findings (≥5)
- [x] Deprecated API detection incluída (AP-13)
- [x] Skill pausa para confirmação

**Fase 3 — Refatoração**
- [x] Estrutura MVC (models/ controllers/ routes/ middlewares/ config/)
- [x] Config extraída (settings.py com env vars)
- [x] Models por domínio
- [x] Rotas separadas e finas
- [x] Controllers concentram lógica
- [x] Error handler centralizado
- [x] Entry point claro (app.py)
- [x] App inicia sem erros
- [x] Endpoints respondem: /health, /produtos, /usuarios, /login

#### Projeto 2 — ecommerce-api-legacy

**Fase 1 — Análise**
- [x] Linguagem detectada: Node.js
- [x] Framework detectado: Express 4.18.2
- [x] Domínio: LMS API
- [x] Arquivos analisados: 3

**Fase 2 — Auditoria**
- [x] Relatório segue template
- [x] Cada finding tem arquivo:linha exatos
- [x] Findings ordenados CRITICAL → LOW
- [x] 14 findings (≥5)
- [x] Deprecated API detection incluída
- [x] Skill pausa para confirmação

**Fase 3 — Refatoração**
- [x] Estrutura MVC (models/ controllers/ routes/ middlewares/ config/)
- [x] Config extraída com env vars
- [x] Models separados por entidade
- [x] Rotas finas delegando a controllers
- [x] Controllers com async/await
- [x] Error handler centralizado
- [x] Entry point claro
- [x] App inicia sem erros
- [x] Endpoints: /api/checkout, /api/admin/financial-report, /api/users/:id

#### Projeto 3 — task-manager-api

**Fase 1 — Análise**
- [x] Linguagem detectada: Python
- [x] Framework detectado: Flask 3.0.0 + SQLAlchemy
- [x] Domínio: Task Manager API
- [x] Arquivos analisados: 13

**Fase 2 — Auditoria**
- [x] Relatório segue template
- [x] Cada finding tem arquivo:linha exatos
- [x] Findings ordenados CRITICAL → LOW
- [x] 14 findings (≥5)
- [x] Deprecated API detection incluída (utcnow, MD5)
- [x] Skill pausa para confirmação

**Fase 3 — Refatoração**
- [x] Controllers criados extraindo lógica das rotas
- [x] Config extraída (settings.py)
- [x] MD5 → bcrypt
- [x] Password removido do to_dict()
- [x] utcnow() → datetime.now(timezone.utc)
- [x] N+1 → joinedload
- [x] is_overdue() do model usado em vez de lógica duplicada
- [x] Error handler centralizado
- [x] App inicia sem erros
- [x] Endpoints: /health, /tasks, /users, /login, /reports/summary, /tasks/search, /tasks/stats, /categories

### Logs das Aplicações Rodando

**code-smells-project:**
```
==================================================
SERVIDOR INICIADO
Rodando em http://0.0.0.0:5000
==================================================
127.0.0.1 - "GET /health HTTP/1.1" 200 - {"database":"connected","status":"ok"}
127.0.0.1 - "GET /produtos HTTP/1.1" 200 - Products: 10
127.0.0.1 - "GET /usuarios HTTP/1.1" 200 - Users: 3
127.0.0.1 - "POST /login HTTP/1.1" 200 - Login: Login OK
```

**ecommerce-api-legacy:**
```
LMS API running on port 3000
POST /api/checkout → {"msg":"Success","enrollment_id":2}
GET /api/admin/financial-report → [2 course reports with revenue data]
DELETE /api/users/1 → {"message":"User and associated records deleted successfully"}
```

**task-manager-api:**
```
127.0.0.1 - "GET /health HTTP/1.1" 200 - {"status":"ok","timestamp":"2026-06-22 15:44:27..."}
127.0.0.1 - "GET /tasks HTTP/1.1" 200 - Tasks: 10
127.0.0.1 - "GET /users HTTP/1.1" 200 - Users: 3
127.0.0.1 - "POST /login HTTP/1.1" 200 - Login: Login successful, User: João Silva
127.0.0.1 - "GET /reports/summary HTTP/1.1" 200 - Total: 10, Overdue: 2
127.0.0.1 - "GET /tasks/stats HTTP/1.1" 200 - Completion rate: 10.0%
127.0.0.1 - "GET /tasks/search?q=bug HTTP/1.1" 200 - Search results: 1
127.0.0.1 - "GET /categories HTTP/1.1" 200 - Categories: 4
```

### Observações Sobre Stacks Diferentes

- **Python/Flask (code-smells-project):** A skill detectou corretamente um monolito de 4 arquivos. A refatoração criou 15+ arquivos em estrutura MVC limpa. O maior ganho foi eliminar SQL injection (15+ queries vulneráveis → 0) e extrair a God Class de 314 linhas.
- **Node.js/Express (ecommerce-api-legacy):** A skill adaptou-se ao ecossistema JS — usou async/await para resolver callback hell, bcrypt para substituir badCrypto, e Express Router para separar rotas. O padrão MVC foi adaptado para usar classes e require/module.exports.
- **Python/Flask parcialmente organizado (task-manager-api):** A skill identificou que o projeto já tinha estrutura mas a lógica estava nos lugares errados. Em vez de reconstruir, criou controllers e moveu a lógica das rotas para lá, preservando os models e ajustando as dependências (bcrypt, timezone-aware datetimes).

---

## D) Como Executar

### Pré-requisitos

- **Claude Code** instalado e configurado (ou Gemini CLI / OpenAI Codex)
- Python 3.10+ (para os projetos Python)
- Node.js 18+ (para o projeto Node.js)

### Projeto 1 — code-smells-project

```bash
cd code-smells-project
pip install -r requirements.txt
claude "/refactor-arch"
```

Validar:
```bash
python app.py
curl http://localhost:5000/health
curl http://localhost:5000/produtos
curl -X POST http://localhost:5000/login -H "Content-Type: application/json" -d '{"email":"admin@loja.com","senha":"admin123"}'
```

### Projeto 2 — ecommerce-api-legacy

```bash
cd ecommerce-api-legacy
npm install
claude "/refactor-arch"
```

Validar:
```bash
npm start
curl -X POST http://localhost:3000/api/checkout -H "Content-Type: application/json" -d '{"usr":"Test","eml":"test@test.com","pwd":"12345678","c_id":2,"card":"4111222233334444"}'
curl http://localhost:3000/api/admin/financial-report
```

### Projeto 3 — task-manager-api

```bash
cd task-manager-api
pip install -r requirements.txt
python seed.py
claude "/refactor-arch"
```

Validar:
```bash
python app.py
curl http://localhost:5000/health
curl http://localhost:5000/tasks
curl http://localhost:5000/reports/summary
```

### Estrutura do Repositório

```
mba-ia-refactor-projects-skill/
├── README.md
├── DESAFIO.md
├── reports/
│   ├── audit-project-1.md
│   ├── audit-project-2.md
│   └── audit-project-3.md
├── code-smells-project/
│   ├── .claude/skills/refactor-arch/
│   │   ├── SKILL.md
│   │   ├── project-analysis.md
│   │   ├── anti-patterns-catalog.md
│   │   ├── audit-report-template.md
│   │   ├── mvc-architecture.md
│   │   └── refactoring-playbook.md
│   ├── config/settings.py
│   ├── models/{product,user,order,report}_model.py
│   ├── controllers/{product,user,order,report}_controller.py
│   ├── routes/{product,user,order,report}_routes.py
│   ├── middlewares/error_handler.py
│   ├── app.py
│   ├── database.py
│   ├── .env.example
│   └── .gitignore
├── ecommerce-api-legacy/
│   ├── .claude/skills/refactor-arch/
│   ├── src/
│   │   ├── config/index.js
│   │   ├── models/{user,course,enrollment,payment}Model.js
│   │   ├── controllers/{checkout,report,user}Controller.js
│   │   ├── routes/{checkout,report,user}Routes.js
│   │   ├── middlewares/errorHandler.js
│   │   ├── database.js
│   │   └── app.js
│   ├── .env.example
│   └── .gitignore
└── task-manager-api/
    ├── .claude/skills/refactor-arch/
    ├── config/settings.py
    ├── controllers/{task,user,report}_controller.py
    ├── models/{task,user,category}.py
    ├── routes/{task,user,report}_routes.py
    ├── services/notification_service.py
    ├── middlewares/error_handler.py
    ├── app.py
    ├── .env.example
    └── .gitignore
```

---

## Critérios de Aceite

| Critério | Projeto 1 | Projeto 2 | Projeto 3 |
|----------|-----------|-----------|-----------|
| Fase 1 detecta stack corretamente | ✓ Python/Flask | ✓ Node.js/Express | ✓ Python/Flask+SQLAlchemy |
| Fase 2 encontra ≥ 5 findings | ✓ 18 findings | ✓ 14 findings | ✓ 14 findings |
| Fase 2 inclui ≥ 1 CRITICAL/HIGH | ✓ 5 CRITICAL | ✓ 3 CRITICAL | ✓ 3 CRITICAL |
| Fase 3 app funciona após refatoração | ✓ All endpoints OK | ✓ All endpoints OK | ✓ All endpoints OK |
