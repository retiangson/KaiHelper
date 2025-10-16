Perfect ✅ — I’ll generate the **full `README.md` and `LICENSE` inline** based on your uploaded `KaiHelper.zip` (which reflects your latest project architecture and refactored code).

---

## 🧾 `README.md`

**Project Title:** KaiHelper – Grocery Budgeting App
**Version:** 1.0.0
**Author:** Ronald Ephraim C. Tiangson

---

### 📘 Overview

**KaiHelper** is a modern AI-powered **Grocery Budgeting App** designed to help families manage grocery spending efficiently.
The backend is built using **FastAPI**, **SQLAlchemy ORM**, and **DTO-based architecture**, following strict **SOLID** and **clean-architecture principles** for clarity, testability, and maintainability.

The system allows users to:

* Create and manage accounts securely (hashed passwords via PBKDF2-SHA256)
* Record, categorize, and analyze expenses
* Automatically extract grocery data from receipt images via **GPT-4o**
* Sync expenses and groceries into a centralized cloud database (AWS RDS)
* Deploy serverless via **AWS Lambda + API Gateway**

---

### 🏗️ Architecture

Layered and modular architecture ensuring separation of concerns:

```
kaihelper/
├── api/                 # FastAPI route handlers (REST endpoints)
├── business/            # Core business logic (services, interfaces)
├── config/              # Environment settings, logging, database config
├── contracts/           # DTOs (Request, Response, Result)
├── domain/              # ORM models, repositories, and mappers
│   ├── core/            # Base database engine/session
│   ├── mappers/         # Mapper classes (Entity <-> DTO)
│   ├── models/          # SQLAlchemy ORM models (User, Expense, etc.)
│   └── repositories/    # Repositories for DB operations
├── tests/               # Unit and integration tests
└── ui/                  # Placeholder for Android / Web UI integration
```

🧩 **Design Principles**

* Follows **Single Responsibility Principle (SRP)**
* Repository pattern abstracts database logic
* DTOs isolate API schemas from domain models
* Mappers convert ORM ↔ DTO consistently
* Configuration handled centrally via `config/settings.py`

---

### ⚙️ Tech Stack

| Layer      | Technology                                 |
| ---------- | ------------------------------------------ |
| Backend    | Python 3.10+, FastAPI, SQLAlchemy ORM      |
| AI Parsing | OpenAI GPT-4o for receipt text extraction  |
| Database   | MySQL / AWS RDS (fallback: SQLite for dev) |
| Security   | PBKDF2-SHA256 password hashing (Passlib)   |
| Deployment | AWS Lambda + API Gateway (Free Tier)       |
| Testing    | Pytest + HTTPX                             |
| Logging    | Python Logging + Uvicorn logs              |

---

### 📦 Installation & Setup

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/ronaldtiangson/KaiHelper.git
cd KaiHelper
```

#### 2️⃣ Create and Activate a Virtual Environment

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

#### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4️⃣ Configure Environment Variables

Create a `.env` file in the project root (or copy `.env.example`):

```env
ENV=development
DB_ENGINE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=kaihelper
OPENAI_API_KEY=your_openai_key_here
```

---

### 🗄️ Database Initialization

> **The app automatically creates tables at runtime if the schema doesn’t exist.**
> To seed default data (admin user, categories, etc.), run the following script.

#### 🧱 Initialize and Seed Database

```bash
python -m kaihelper.domain.scripts.seed_data
```

This script will:

* Ensure the database exists (create if missing)
* Create tables based on models
* Insert default records (admin account, sample categories)

🧩 **Example Default Admin Account**

| Username | Email               | Password |
| -------- | ------------------- | -------- |
| `admin`  | `admin@example.com` | `admin`  |

(Password automatically hashed using PBKDF2-SHA256.)

---

### 🚀 Running the API

#### Run via Uvicorn (development)

```bash
uvicorn kaihelper.api.main_api:app --reload --host 127.0.0.1 --port 8000
```

Access the API at:
➡️ **[http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)**
Swagger UI available at:
➡️ **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

### 🧠 Key Endpoints

| Endpoint               | Method | Description                                 |
| ---------------------- | ------ | ------------------------------------------- |
| `/api/users/register`  | `POST` | Register new user                           |
| `/api/users/login`     | `POST` | Authenticate user                           |
| `/api/categories/`     | `GET`  | Retrieve list of categories                 |
| `/api/receipts/upload` | `POST` | Upload and parse receipt image using GPT-4o |
| `/api/expenses/`       | `GET`  | Get user expenses                           |
| `/api/groceries/`      | `GET`  | List grocery items                          |

**Example Request**

```bash
curl -X POST http://127.0.0.1:8000/api/users/login \
-H "Content-Type: application/json" \
-d '{"username_or_email":"admin","password":"admin"}'
```

---

### 🧩 Testing

Run all tests (unit + integration):

```bash
pytest
```

Typical structure:

```
kaihelper/tests/
├── test_users.py
├── test_categories.py
├── test_receipts.py
└── __init__.py
```

---

### ☁️ Deployment (AWS Free Tier)

1. Package with dependencies using `serverless` or `Zappa` for Lambda.
2. Configure API Gateway for route proxying to FastAPI.
3. Set `DB_HOST`, `DB_USER`, and `DB_PASSWORD` to AWS RDS credentials.
4. Configure environment variables in Lambda.
5. Test deployed endpoint via API Gateway URL.

Example AWS RDS config:

```env
DB_ENGINE=mysql
DB_HOST=mykaihelper.c123abc.us-east-1.rds.amazonaws.com
DB_USER=admin
DB_PASSWORD=securepass123
DB_NAME=kaihelper
```

---

### 📊 Example Data Flow

1. User uploads receipt → `/api/receipts/upload`
2. GPT-4o parses text and returns extracted items
3. System identifies **receipt category** (e.g., Groceries)
4. Expense and groceries are saved in DB
5. Response returns summary (category, total, items)

---

### 🧱 Folder Explanations

| Folder                 | Description                                         |
| ---------------------- | --------------------------------------------------- |
| `business/interfaces/` | Abstract definitions (service contracts)            |
| `business/services/`   | Implementations of service logic                    |
| `contracts/`           | Data transfer objects (DTOs) for requests/responses |
| `domain/core/`         | Database engine and session setup                   |
| `domain/models/`       | SQLAlchemy ORM models                               |
| `domain/mappers/`      | Entity ↔ DTO transformation                         |
| `domain/repositories/` | Database query abstraction                          |
| `config/settings.py`   | Loads `.env` variables into `settings` object       |
| `api/`                 | FastAPI routes (entry points)                       |
| `tests/`               | Automated test suites                               |
| `ui/`                  | Android / Web UI integration layer                  |

---

### 🧰 Developer Notes

* Always import DTOs in endpoints (not ORM models)
* Use `ResultDTO.success()` / `.error()` for consistent API responses
* All passwords must be hashed before saving
* Use `SessionLocal()` from `domain/core/database.py` for transactions

---

### 🧾 License

This project is distributed under the MIT License (see below).

---

### 👥 Contributors

| Name                           | Role                 | Description                                                                                    |
| ------------------------------ | ---------------------| ---------------------------------------------------------------------------------------------- |
| **Fredierick Saladas**         | Principal Engineer   | System design optimization, database performance tuning, and infrastructure scalability review |
| **Ronald Ephraim Tiangson**    | Lead Engineer        | Architecture, backend development, AI integration                                              |


---

### 🗓️ Version History

| Version | Date       | Changes                                                     |
| ------- | ---------- | ----------------------------------------------------------- |
| 1.0.0   | 2025-10-17 | Initial FastAPI backend release, GPT-4o receipt integration |

---

### 💡 Future Enhancements

* [ ] Multi-currency support
* [ ] Budget alerts via email
* [ ] Monthly spending dashboard (React UI)
* [ ] Receipt OCR fallback (Tesseract)
* [ ] Offline mode via SQLite sync

---

## 📜 LICENSE

```
MIT License

Copyright (c) 2025 Ronald Ephraim C. Tiangson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```