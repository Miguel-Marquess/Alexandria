# Alexandria

<p align="center">
  <img src="docs/assets/alexandria-banner.png" alt="Alexandria" width="850">
</p>

<p align="center">
  A library management system built with Python and FastAPI.
</p>

---


## 📖 About

**Alexandria** is a library management system developed as a monolithic backend application using **FastAPI**.

The project provides an API for managing the main resources and operations of a library, including users, books, authors, and loans.

The main goal of the project is to build a maintainable backend while applying software engineering practices such as:

* Separation of responsibilities
* Business logic isolation
* Data validation
* Relational database modeling
* Database migrations
* Automated testing
* Authentication and authorization
* Containerized development
* Type safety and maintainability

---

## 🚀 Technology Stack

### Backend

* **[Python](https://www.python.org/)** — Main programming language.
* **[FastAPI](https://fastapi.tiangolo.com/)** — Web framework used to build the REST API.
* **[Pydantic](https://docs.pydantic.dev/)** — Data validation and serialization.
* **[SQLAlchemy](https://www.sqlalchemy.org/)** — ORM and database interaction.
* **[Psycopg](https://www.psycopg.org/)** — PostgreSQL database adapter.

### Database

* **[PostgreSQL](https://www.postgresql.org/)** — Relational database used for data persistence.
* **[Alembic](https://alembic.sqlalchemy.org/)** — Database schema migration tool.

### Development & Infrastructure

* **[Poetry](https://python-poetry.org/)** — Dependency and project management.
* **[Docker](https://www.docker.com/)** — Containerization.
* **[Pytest](https://docs.pytest.org/)** — Automated testing framework.

---

## 🏗️ Architecture

Alexandria follows a layered application structure in order to separate HTTP handling, business rules, data access, and persistence.

The exact responsibilities and architectural decisions are described in the [Architecture documentation](docs/architecture.md).

<p align="center">
  <img src="docs/assets/architecture.png" alt="Alexandria architecture" width="850">
</p>

---


## 📡 API

Alexandria exposes its functionality through a REST API built with FastAPI.

FastAPI automatically provides interactive API documentation through Swagger UI and ReDoc.

After starting the application, access:

* **Swagger UI:** `http://127.0.0.1:8000/docs#/`

More detailed API information is available in the [API Documentation](docs/api.md).

---

## 📁 Project Structure

The project is organized to separate application responsibilities and infrastructure components.

```text
.
├── docs/
│   └── assets/
│
├── library_management/
│   ├── depends/
│   ├── exceptions/
│   ├── models/
│   ├── repository/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── app.py
│   ├── database.py
│   ├── security.py
│   └── settings.py
│
├── migrations/
│
├── tests/
│   ├── test_books/
│   ├── test_services/
│   ├── test_users/
│   ├── conftest.py
│   ├── test_app.py
│   ├── test_auth.py
│   └── test_db.py
│
├── .env.example
├── .gitignore
├── alembic.ini
├── compose.yml
├── Dockerfile
├── entrypoint.sh
├── poetry.lock
├── pyproject.toml
└── README.md
```

---

## 🔐 Environment Variables

Alexandria uses environment variables for application configuration and database credentials.

Create a `.env` file based on `.env.example`.

| Variable                      | Description                                  | Example                                                        |
| ----------------------------- | -------------------------------------------- | -------------------------------------------------------------- |
| `DATABASE_URL`                | PostgreSQL connection URL                    | `postgresql+psycopg://user:password@library_database:5432/alexandria` |
| `TOKEN_SECRET_KEY`                  | Secret key used by the authentication system | `your-secret-key`                                              |
| `ACCESS_TOKEN_EXPIRE_MINUTES_TIME` | Access token expiration time                 | `30`                                                           |
| `ALGORITHM`                  | Algorithm used for JWT signing and verification                |  `HS256`                     |
| `MAX_VALUE_LOANS`                  | Max user loans        |  `2`                     |
| `POSTGRES_USER`                  | Database user        |  `your-dabatase-user`                 |
| `POSTGRES_DB`                  | Database name        |  `your-dabatase-name`                    |
| `POSTGRES_PASSWORD`                  | Database password        |  `your-dabatase-password`               |

---

## 🛠️ Installation

### Prerequisites

Make sure the following tools are installed:

* Python `3.14+`
* Poetry
* Docker
* Docker Compose

### Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### Install dependencies

```bash
poetry install
```

### Configure environment variables

```bash
cp .env.example .env
```

Configure the required values in `.env`.

### Start the application

```bash
docker compose up -d
```

> The application entrypoint automatically applies pending database migrations before starting the API.

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## 🧪 Testing

Automated tests are written using **Pytest**.

Run the complete test suite:

```bash
poetry run task test
```

The test suite focuses on application behavior, business rules, and integration between the main components of the system.

---

## 🔧 Development

Poetry is used to manage the project's Python environment and dependencies.

Install a dependency:

```bash
poetry add <package>
```

Install a development dependency:

```bash
poetry add --group dev <package>
```

Run a command through the project's environment:

```bash
poetry run <command>
```

### Database migrations

Create a migration:

```bash
poetry run alembic revision --autogenerate -m "description"
```

Apply migrations:

```bash
poetry run alembic upgrade head
```

Rollback the latest migration:

```bash
poetry run alembic downgrade -1
```

---

## 📚 Documentation

Detailed technical documentation is maintained separately from the main README.

| Document                                  | Description                                                 |
| ----------------------------------------- | ----------------------------------------------------------- |
| [Architecture](docs/architecture.md)      | Application architecture and separation of responsibilities |
| [Database](docs/database.md)              | Entities, relationships, and database design                |
| [Authentication](docs/authentication.md)  | Authentication and authorization implementation             |
| [API](docs/api.md)                        | API endpoints and usage                                     |
| [Changelog](docs/changelog.md)            | Project changes and development history                     |
| [Architecture Decisions](docs/decisions/) | Relevant technical and architectural decisions              |

---

## 📌 Project Status

Alexandria is currently under active development.

---

