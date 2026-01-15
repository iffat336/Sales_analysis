# API Integration Strategy

## 1. Link Frontend & Backend
We have successfully linked the dashboard interaction to the backend logic.

### Technology: Fetch API
Instead of Axios (which requires an external library import), we used the native browser **Fetch API**. This is the modern standard equivalent to XHR/AJAX.

*   **Implementation**: In `frontend/script.js`, we have async functions like `fetchMonthlySales()` that call the backend.
*   **Base URL**: We configured `API_URL` to be relative (`""`), allowing the frontend to automatically talk to the backend serving it, regardless of the domain name.

## 2. Handling Request Types

We have implemented both **GET** and **POST** requests as required.

### GET Requests (Data Retrieval)
Used for fetching data to populate charts and tables without modifying the server state.

*   **Example Code** (`script.js`):
    ```javascript
    const response = await fetch(`${API_URL}/analytics/monthly-sales`);
    const data = await response.json();
    // Uses data to render Chart.js buffer
    ```
*   **Use Cases**:
    *   Loading Monthly Sales Trend.
    *   Loading Top 10 Customers.
    *   Loading Recent Transactions table.

### POST Requests (Actions)
Used for performing actions that change the server state (mutations).

*   **Example Code** (`script.js`):
    ```javascript
    const response = await fetch(`${API_URL}/system/rebuild-database`, {
        method: 'POST'
    });
    ```
*   **Use Case**:
    *   **Rebuild Database**: The "Rebuild" button sends a POST request to trigger the Python script. This ensures that destructive actions are not triggered accidentally by web crawlers (which only do GETs).

### Error Handling
We wrapped all API calls in `try/catch` blocks (Example: `console.error`) and used `alert()` to notify users of critical failures (like a failed database rebuild).
