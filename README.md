# Sales Analysis Dashboard 📊

A full-stack data science application analyzing the "Online Retail II" dataset.
It features a **FastAPI Backend**, a **Glassmorphism Frontend**, and a **Streamlit Dashboard**.

## 🚀 Two Ways to Deploy

This repository is set up to be deployed on **BOTH** Heroku and Streamlit Cloud simultaneously.

### Option 1: The Full Stack App (Heroku / Docker)
*   **What it is**: The custom-built Backend (FastAPI) + Frontend (HTML/JS).
*   **Entry Point**: `backend/main.py` (via `Procfile`)
*   **Deployment**:
    1.  Create an app on Heroku.
    2.  Connect this GitHub repo.
    3.  Deploy `main` branch.
*   **Live View**: A responsive, dark-mode dashboard.

### Option 2: The Streamlit App (Streamlit Cloud)
*   **What it is**: A pure Python dashboard using `streamlit` and `plotly`.
*   **Entry Point**: `streamlit_app.py`
*   **Deployment**:
    1.  Go to [share.streamlit.io](https://share.streamlit.io).
    2.  Connect this GitHub repo.
    3.  Select `streamlit_app.py` as the main file.
*   **Live View**: Interactive Plotly charts and dataframes.

---

## 📂 Project Structure
*   `backend/`: FastAPI application (API, Database logic).
*   `frontend/`: Vanilla JS/CSS Dashboard.
*   `data/`: Contains the dataset `online_retail_II.xlsx`.
*   `sales_analysis.db`: The SQLite database (pre-populated).
*   `streamlit_app.py`: The standalone Streamlit version.

## 🛠 Documentation
We have detailed documentation for every part of this system:
*   [Database Design](database_design.md): Schema and SQL choices.
*   [Backend Architecture](backend_architecture.md): FastAPI and ORM details.
*   [Frontend Design](frontend_design.md): UI/UX and JS logic.
*   [API Integration](api_integration.md): How frontend talks to backend.
*   [Final Report & Scalability](final_project_report.md): Future roadmap.

## 💻 Running Locally

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Full Stack (Backend + Frontend)
```bash
uvicorn backend.main:app --reload
# Open http://127.0.0.1:8000
```

### 3. Run Streamlit Version
```bash
streamlit run streamlit_app.py
```
