# 3. Project Materials

## 3.1 Software and Tools

The project uses a Python web application with server-rendered HTML and a PostgreSQL database. Table 1 lists the software and tools selected for development. Python package versions reflect the supplied dependency output; platform and frontend versions follow the project specification.

**Table 1. Software, versions, and purposes**

| Software or tool | Version | Purpose |
|---|---|---|
| Python | 3.13 | Application programming language |
| FastAPI | 0.143.0 | HTTP routes, form handling, and dependency injection |
| Uvicorn | 0.54.0 | Application server |
| SQLAlchemy | 2.1.4 | Synchronous database access and ORM models |
| PostgreSQL | 16 | Relational storage and reservation range constraints |
| psycopg | 3.3.6 | PostgreSQL database driver |
| Jinja2 | 3.1.6 | Server-rendered HTML templates |
| pydantic-settings | 2.15.0 | Application settings loaded from environment variables |
| python-multipart | 0.0.32 | Form data parsing |
| pwdlib with Argon2 | 0.3.1 | Password hashing and verification |
| itsdangerous | 2.2.0 | Signing support for cookie-based sessions |
| Bootstrap | 5.3 | Page layout and form styling through a CDN |
| Leaflet | Stable 1.x | Interactive maps using OpenStreetMap tiles |
| pytest | 9.1.1 | Automated testing |
| httpx2 | 2.13.1 | HTTP support for application tests |
| Ruff | 0.17.0 | Code formatting and linting |
| uv; Docker Compose; Git and GitHub | Not specified | Dependency management; database setup; version control and review |

## 3.2 System Architecture

The system is a single-process monolithic application organized into three layers: routers, services, and models. Routers handle HTTP requests, receive validated input, enforce access through dependencies, and return Jinja2 pages or redirects. Services contain business rules and database operations. Models define database tables and relationships. Dependencies flow from routers to services and then to models.

Database access is synchronous. During development, PostgreSQL runs through Docker Compose, while the application runs locally using uv. The interface uses Bootstrap and server-rendered HTML. Leaflet displays vehicle locations on OpenStreetMap tiles and supports filtering within the visible map area. Authentication uses signed session cookies, and authorization distinguishes customers from company users. Fleet operations restrict each company to its own vehicles.

## 3.3 Data Model

The database contains three related tables: `users`, `cars`, and `reservations`. The `users` table stores account details, password hashes, and the `customer` or `company` role. A company is represented by a user with a company name.

Each car belongs to a company user through `cars.owner_id`. Vehicle records contain descriptive attributes, seating capacity, daily rental price, location coordinates, an optional image URL, and an active flag. Each reservation references a customer through `user_id` and a vehicle through `car_id`.

Reservation periods use PostgreSQL `DATERANGE` values with half-open boundaries, `[start, end)`. Prices use `Numeric(10, 2)` and Python `Decimal`, with amounts expressed in TL. Each reservation stores its total price at booking time, its status, and only the last four card digits. Full card numbers, expiry dates, and CVVs are never stored. Vehicles are deactivated and reservations are cancelled rather than deleted.

## 3.4 Methods

### Concurrency Control

### LLM-Based Recommendations
