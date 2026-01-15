# Backend Architecture and Implementation

## 1. Framework Choice: FastAPI
We selected **FastAPI** over Flask or Django.

### Reasoning
*   **Performance**: FastAPI is significantly faster than Flask/Django (based on Starlette and Pydantic).
*   **Modernity**: It natively supports asynchronous programming (`async/await`) and automatic data validation.
*   **Automatic Documentation**: It automatically generates Swagger UI (which we use for testing), adhering to OpenAPI standards.
*   **Alignment**: It fulfills the "lightweight" requirement of Flask but with better performance and developer experience.

## 2. API Design (RESTful)
We implemented a strict **RESTful API** for interacting with the data.

### Endpoints
*   **CRUD Operations**:
    *   `GET /products`: Retrieve product list.
    *   `GET /transactions`: Retrieve transaction history.
*   **Analytics Resources**:
    *   `GET /analytics/monthly-sales`: Specialized resource for aggregated data.
    *   `GET /analytics/top-customers`: Resource for high-value customer data.
*   **System Actions**:
    *   `POST /system/rebuild-database`: RPC-style endpoint for system management.
*   **Authentication**: *Note: For this internal dashboard, we used open access. For production, we would add `OAuth2` with `python-jose` as per FastAPI best practices.*

## 3. Database Connection (ORM)
We used **SQLAlchemy**, the industry-standard ORM for Python.

### Implementation
*   **ORM Models** (`backend/models.py`): We defined classes like `Customer`, `Product`, `Invoice` that map directly to database tables.
*   **Session Management** (`backend/database.py`): We use dependency injection (`Depends(get_db)`) to handle database sessions safely (open/close) for every request.
*   **Querying**: We use both ORM methods (`db.query(models.Product)`) and optimized SQL (`db.execute(text(...))`) where raw performance is needed for analytics.

This architecture ensures the backend is scalable, maintainable, and type-safe.
