# Frontend Development and Design

## 1. Framework Choice: Vanilla HTML/CSS/JS
We selected **Vanilla HTML/CSS/JavaScript** instead of React.

### Reasoning
*   **Simplicity**: As per your criteria, we chose the path for "simpler projects". React adds complexity (Node.js build steps, Webpack, Babel) which is unnecessary for a dashboard with ~4 main views.
*   **Performance**: Vanilla JS is the fastest possible option as there is no framework overhead or Virtual DOM diffing needed for this dataset size.
*   **Integration**: It works instantly with the FastAPI backend. You can open the HTML file directly or serve it via Python without a separate frontend server process.

## 2. Frontend Design (UI/UX)
We implemented a **Modern Glassmorphism** design that is both intuitive and responsive.

### User-Friendly Features
*   **Intuitive Layout**: We used a standard dashboard layout (KPIs at top, Charts in middle, Data at bottom) which users instantly understand.
*   **Visual Feedback**: Buttons have hover states, and we added a "Loading Spinner" for the database rebuild action so users know the system is working.
*   **Dark Mode**: Reduces eye strain and provides a premium, "Data Science" aesthetic.

### Responsiveness (Mobile & Desktop)
*   **CSS Grid & Flexbox**: We used `grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))` for the KPI cards.
    *   *Desktop*: Cards align in a row.
    *   *Mobile*: Cards automatically stack vertically.
*   **Charts**: Chart.js canvases are wrapped in responsive containers that resize based on the screen width.
*   **Navigation**: The header flex-wraps on small screens to ensure the title and buttons remain accessible.

This approach delivers a high-quality user experience without the technical debt of a complex frontend framework.
