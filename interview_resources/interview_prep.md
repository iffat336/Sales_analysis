# Interview Prep: Thorin Schiffer

## 1. Interviewer Profile Analysis
*   **Name**: Thorin Schiffer
*   **Likely Role**: Senior Python Developer / Cloud Engineer (AWS)
*   **Location**: Amsterdam (likely European work culture: direct, quality-focused).
*   **Key Skills**: **Python**, **AWS**, **Software Architecture**.

### 💡 Insight
Since he is a Python/AWS expert, he will not just ask "does it work?". He will ask **"is it built right?"**. He will care about:
*   **Code Structure**: Type hinting, modularity (which we did).
*   **Dependency Management**: `requirements.txt` vs Poetry.
*   **Deployment**: How to get this running in the cloud (Docker/AWS).

---

## 2. Likely Questions He Will Ask You (And Answers)

### Q1: "Why did you choose FastAPI over Flask or Django?"
*   **Bad Answer**: "It's popular."
*   **Good Answer**: "I needed high performance for the analytics endpoints. FastAPI provides asynchronous support (`async/await`) out of the box, which is perfect for I/O bound database operations. Plus, the automatic openAPI generation helped me verify my endpoints quickly without writing separate documentation."

### Q2: "Your dataset is in SQLite. How would you scale this for production on AWS?"
*   **Your Answer**: "SQLite is great for this standalone analysis, but for production, I would migrate to **AWS RDS (PostgreSQL)**. I would update the `database.py` connection string to point to the RDS instance. For the application, I would deploy the Docker container to **AWS ECS (Fargate)** or **App Runner** to handle auto-scaling."

### Q3: "Explain your database normalization choice."
*   **Your Answer**: "I used a Star Schema approach. I separated `Customers`, `Products`, and `Invoices` to eliminate data redundancy. This ensures that if a customer updates their name, I only change it in one row, not in 1,000 transaction rows. It guarantees data integrity."

### Q4: "How do you ensure your code is good quality?"
*   **Your Answer**: "I use **Type Hinting** (Pydantic models) to enforce data schemas. I also wrote integration tests (`test_backend.py`) to verify that every API endpoint returns a 200 OK status before I commit."

---

## 3. Questions YOU Should Ask Him
*Asking technical questions shows you are a peer, not just a junior.*

1.  **"I noticed you have strong AWS experience. Does your team prefer Serverless (Lambda) for Python microservices, or do you stick to containerized services (ECS/EKS)?"**
    *   *Why ask this*: It shows you know the difference and care about architecture.
2.  **"How does your team handle Python dependency management? Do you use `pip`, `poetry`, or something else?"**
    *   *Why ask this*: It's a common pain point in Python; asking about it shows practical experience.
3.  **"What is the biggest data engineering challenge your team is facing right now?"**

---

## 4. Your "Elevator Pitch" for the Project
*"I built a full-stack sales analytics platform. It parses raw Excel data into a normalized SQL database, serves insights via a FastAPI REST backend, and visualizes them with a custom Glassmorphism frontend. It’s fully containerized with Docker for easy deployment."*
