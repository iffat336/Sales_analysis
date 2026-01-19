# Python Developer Interview Q&A Guide
**Target Interviewer:** Thorin Schiffer (Senior Python/AWS Developer)
**Role:** Python Developer

This guide covers the full spectrum of questions a Senior Dev will ask, from Core Python to Cloud Architecture.

---

## 🐍 1. Core Python (The Basics & Advanced)

### Q: What is the Global Interpreter Lock (GIL) and how does it affect concurrency?
*   **Answer**: "The GIL is a mutex that prevents multiple native threads from executing Python bytecodes at once. This means Python threads are not true parallel threads on multi-core CPUs.
    *   **Impact**: It limits CPU-bound tasks (like heavy math).
    *   **Workaround**: For CPU-bound tasks, I use `multiprocessing` (separate processes). For I/O-bound tasks (like API calls), I use `asyncio` or threading, where the GIL is released during I/O wait times."

### Q: Explain the difference between `list` and `tuple`.
*   **Answer**: "Lists are mutable (can change), tuples are immutable (cannot change). Tuples are slightly faster and hashable (can be used as dictionary keys), whereas lists cannot."

### Q: What are Generators and `yield`?
*   **Answer**: "Generators are functions that return an iterator (using `yield`) instead of returning all values at once (`return`). They are memory efficient because they produce items one by one on the fly, rather than storing a huge list in RAM."

### Q: What is a Decorator?
*   **Answer**: "A decorator is a function that takes another function and extends its behavior without modifying it constantly. I use them often for things like `@login_required` or logging execution time."

---

## 🚀 2. Frameworks & Backend (FastAPI / Web)

### Q: Why FastAPI over Flask/Django? (Thorin's Favorite)
*   **Answer**: "FastAPI is built on **Starlette** (ASGI) and **Pydantic**.
    1.  **Speed**: It's one of the fastest Python frameworks.
    2.  **Async**: Native `async/await` support handles high concurrency better than Flask's synchronous nature.
    3.  **Validation**: Pydantic handles data validation automatically, reducing boilerplate code."

### Q: What is Dependency Injection in FastAPI?
*   **Answer**: "It's a system to declare dependencies (like database sessions or current user) as function parameters. FastAPI creates usage of them only when needed. For example, `def get_user(db: Session = Depends(get_db)):` ensures I get a fresh DB session that automatically closes after the request."

---

## 🗄️ 3. Databases (SQL & ORM)

### Q: What is the N+1 problem in ORMs?
*   **Answer**: "It happens when you fetch a list of parent objects (1 query) and then iterate through them to fetch a related child object (N queries).
    *   **Fix**: Use Eager Loading (e.g., `.options(joinedload(Model.child))` in SQLAlchemy) to fetch everything in a single JOIN query."

### Q: ACID properties - what are they?
*   **Answer**: "Atomicity (All or nothing), Consistency (Data is valid), Isolation (Transactions don't interfere), Durability (Saved data stays saved)."

---

## ☁️ 4. Cloud & DevOps (AWS / Docker)

### Q: How do you handle secrets (API Keys, DB Passwords)?
*   **Answer**: "Never in the code (`.env` file). In production (AWS), I use **AWS Secrets Manager** or Environment Variables injected into the Docker container at runtime."

### Q: Docker vs Virtual Environments?
*   **Answer**: "Virtual Envs isolate Python dependencies. Docker isolates the *entire OS* (libraries, system dependencies). Docker guarantees 'It works on my machine' means 'It works on the server'."

### Q: How would you architect a serverless Python backend?
*   **Answer**: "I would use **AWS Lambda** triggered by **API Gateway**. I'd use layers for heavy libraries (Pandas) to keep the function size small. For the database, I'd use DynamoDB or Aurora Serverless."

---

## 🤝 5. Behavioral & Soft Skills

### Q: Tell me about a time you disagreed with a senior developer.
*   **Answer**: "On a previous project, a senior wanted to put logic in the Database (Stored Procedures). I advocated for keeping logic in the Python Application layer for better version control and testing. I demonstrated this by writing a small prototype showing how much easier it was to unit test the Python code vs the SQL procedure. We compromised by keeping complex aggregations in SQL but business rules in Python."

### Q: How do you handle a bug in production?
*   **Answer**: "First, **Rollback** to the last stable state to restore service. Then, reproduce the bug locally using logs. Fix it, write a **Regression Test** to ensure it doesn't happen again, and then redeploy."

---

## ⁉️ 6. Questions YOU Should Ask Thorin

1.  "With your AWS background, do you prefer **Infrastructure as Code** tools like Terraform or AWS CDK for your Python projects?"
2.  "How does the team balance **Technical Debt** vs **New Features**? Do you have 'cleanup sprints'?"
3.  "What does 'Senior' level code look like to you? Is it about clever one-liners, or readable maintainable structures?"
