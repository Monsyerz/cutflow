# CutFlow

**Smarter cuts. Less waste.**

CutFlow is a web-based, one-dimensional material cutting optimizer built with **Python, Flask, PostgreSQL, and JavaScript**. It uses the **First Fit Decreasing (FFD)** heuristic, supported by a custom Merge Sort implementation, to arrange required cuts into stock pieces and estimate material waste.

The project connects my engineering background with software engineering concepts: algorithms, REST APIs, input validation, relational databases, ORM, database migrations, automated testing, and error handling.

> **Status:** Active development. The application runs locally; public deployment is planned.
>
> **Testing:** 51 automated `unittest` test methods currently in the repository (13 optimizer, 23 Flask route, and 15 API tests).

## Features

### Cutting Optimization

- Enter a stock length and multiple cut lengths with quantities.
- Add or remove cut rows dynamically using JavaScript.
- Expand requested quantities into individual cuts.
- Sort cuts in descending order using a custom Merge Sort implementation.
- Allocate cuts using the First Fit Decreasing (FFD) heuristic.
- Calculate the total number of cuts, total cut length, stock pieces used, material waste, and utilization percentage.
- Display an optimization summary and a proportional visual example of the last stock piece.
- Use Python `Decimal` arithmetic for stock-capacity comparisons, waste, and utilization calculations to avoid common floating-point precision errors.

### REST API

- Optimize cuts programmatically using **`POST /api/optimize`** with a JSON request body.
- Return a JSON summary containing `stocks_used`, `total_cuts`, `total_cut_length`, `waste`, and `utilization`.
- Validate the JSON body, `cuts` list, individual cut objects, numeric lengths, and integer quantities.
- Reject zero, negative, non-finite (`NaN`, `Infinity`), or oversized cuts.
- Enforce a limit of **1,000 total cuts per request**, including quantities across multiple line items.
- Return HTTP **400** with a JSON `error` message for supported validation failures.
- Keep the API calculation separate from database persistence: **the API does not save results to history**.

### Validation and Reliability

- Validate stock lengths, cut lengths, and quantities on the backend, alongside HTML form validation.
- Reject missing, invalid, non-positive, and non-finite length values.
- Reject non-integer or non-positive quantities; reject mismatched form cut/quantity lists.
- Prevent individual cuts from exceeding the stock length.
- Limit each optimization to 1,000 cuts in both the HTML form and REST API.
- Preserve submitted form values after validation errors.
- Roll back failed database writes and display user-friendly error messages.
- Handle database query failures when displaying history or exporting CSV.

### Persistence and History

- Save **web-form optimization summaries** in PostgreSQL using Flask-SQLAlchemy.
- Manage schema changes with Flask-Migrate and Alembic.
- Display the **10 most recent** optimization summaries on the History page, ordered by creation date.
- Export **all saved optimization summaries** to a downloadable CSV file, ordered newest first.
- Export a CSV header row even when the database has no optimization records.

## Example

```text
Stock Length: 20

Required Cuts:
15   × 2
10.5 × 3
7    × 1
5    × 2

Optimization Summary:
Total Stocks:        5
Total Cuts:          8
Total Cut Length:    78.50
Total Waste:         21.50
Overall Utilization: 78.50%

Cutting Layout:
Stock 1: 15 + 5
Stock 2: 15 + 5
Stock 3: 10.5 + 7
Stock 4: 10.5
Stock 5: 10.5
```

The layout above illustrates the optimization result. The current web interface displays an example visualization of the **last stock piece**, not a complete visualization of every stock piece.

## How It Works

1. The user submits a stock length and one or more cut length/quantity pairs through the web form or the REST API.
2. Flask validates the submitted values. The web form preserves inputs if validation fails; the API returns JSON errors.
3. `expand_cuts()` converts quantities into a list of individual cuts.
4. `merge_sort()` sorts the cuts in descending order.
5. `optimize_cuts()` applies **First Fit Decreasing**: each cut is placed in the first existing stock piece with enough capacity; otherwise, a new stock piece is created.
6. `calculate_waste()` and `calculate_utilization()` compute material metrics.
7. **Web form only:** SQLAlchemy saves the summary to PostgreSQL; a failed write triggers a session rollback.
8. The web interface renders results with Jinja2, while the API returns a JSON summary without saving to the database.

### Why Decimal?

Ordinary binary floating-point arithmetic can produce results such as:

```python
0.2 + 0.1 == 0.3  # False
```

That could incorrectly cause an exact-fit combination to occupy two stock pieces or produce a tiny negative waste value.

CutFlow converts numeric inputs to `Decimal` using their string representation during capacity checks and metric calculations, then returns standard numeric result types to the rest of the application.

A regression test covers this case:

```python
stocks = optimize_cuts([0.2, 0.1], 0.3)

assert stocks == [[0.2, 0.1]]
assert calculate_waste(stocks, 0.3) == 0
assert calculate_utilization(stocks, 0.3) == 100
```

**Note:** FFD is a heuristic, not an exact optimization algorithm. It does not guarantee a globally optimal cutting layout for every input.

## Tech Stack

| Area | Technologies |
| --- | --- |
| Backend and API | Python, Flask, JSON |
| Database | PostgreSQL, psycopg, SQLAlchemy, Flask-SQLAlchemy |
| Migrations | Flask-Migrate, Alembic |
| Frontend | HTML, CSS, JavaScript, Jinja2 |
| Testing | unittest, unittest.mock, Flask test client, SQLite (in-memory) |
| Development | Git, GitHub, VS Code, python-dotenv |

## Project Structure

```text
cutflow/
├── app/
│   ├── static/
│   │   ├── styles.css
│   │   └── script.js
│   ├── templates/
│   │   ├── index.html
│   │   └── history.html
│   ├── __init__.py
│   ├── db_models.py
│   ├── extensions.py
│   ├── models.py
│   ├── optimizer.py
│   └── routes.py
├── migrations/
│   └── versions/
├── tests/
│   ├── test_api.py
│   ├── test_optimizer.py
│   └── test_routes.py
├── .gitignore
├── README.md
├── requirements.txt
└── run.py
```

## Database and Endpoints

### OptimizationResult Model

| Field | Type | Purpose |
| --- | --- | --- |
| `id` | Integer | Primary key |
| `stocks_used` | Integer | Number of stock pieces used |
| `waste` | Float | Remaining material waste |
| `utilization` | Float | Utilization percentage |
| `created_at` | DateTime | Timestamp for ordering history |

Currently, the database stores **optimization summaries only**, not full cutting layouts or original input values. `Decimal` is used during calculations, while persisted waste and utilization fields remain SQLAlchemy `Float` columns.

### Routes

| Route | Method | Behavior |
| --- | --- | --- |
| `/` | GET | Display the optimizer form |
| `/` | POST | Validate form inputs, optimize cuts, save summary, and render results |
| `/history` | GET | Display the latest 10 saved summaries |
| `/export` | GET | Download all saved summaries as `history.csv` |
| `/api/optimize` | POST | Validate JSON, optimize cuts, and return a summary **without saving it** |

The CSV export contains `ID`, `Stocks Used`, `Waste`, `Utilization`, and `Created At`. If its database query fails, the application returns an error page with HTTP **503** instead of a CSV download.

### REST API — `POST /api/optimize`

Send a JSON object containing `stock_length` and a non-empty `cuts` array. Each cut must have a `length` and a positive integer `quantity`. Lengths are converted to floating-point numbers and must be finite, greater than zero, and no longer than `stock_length`.

**Example request:**

```http
POST /api/optimize
Content-Type: application/json
```

```json
{
  "stock_length": 20,
  "cuts": [
    {"length": 15, "quantity": 2},
    {"length": 5, "quantity": 2}
  ]
}
```

**Example successful response (`200 OK`):**

```json
{
  "stocks_used": 2,
  "total_cuts": 4,
  "total_cut_length": 40.0,
  "waste": 0.0,
  "utilization": 100.0
}
```

**Example validation response (`400 Bad Request`):**

```json
{
  "error": "Invalid cut quantity"
}
```

**Try it locally** after starting the Flask server (example for Git Bash):

```bash
curl -X POST http://127.0.0.1:5000/api/optimize \
  -H "Content-Type: application/json" \
  -d '{"stock_length":20,"cuts":[{"length":15,"quantity":2},{"length":5,"quantity":2}]}'
```

**Validation behavior:**

| Input | Outcome |
| --- | --- |
| Non-object JSON body, such as `[]` | `400` — `JSON body must be an object` |
| Missing, non-list, or empty `cuts` | `400` — cuts list error |
| A cut entry is not an object | `400` — `Each cut must be a dictionary` |
| Missing `length` or `quantity` within a cut | `400` — required-fields error |
| Invalid, zero, negative, or non-finite lengths | `400` — length error |
| Cut longer than the stock | `400` — `Cut length exceeds stock length` |
| Quantity is not a positive JSON integer | `400` — `Invalid cut quantity` |
| Total `quantity` exceeds 1,000 | `400` — `Too many cuts requested. Please limit to 1000 cuts.` |

For length inputs, numeric strings such as `"20"` are accepted through `float()` conversion. For `quantity`, the API requires a JSON integer: a fraction such as `2.5` and a string such as `"2"` are rejected.

Flask may return its own HTTP error response for malformed JSON syntax or an unsupported request content type; those framework-level errors do not necessarily use the API's JSON `error` format.

## Automated Testing

There are **51 automated test methods** in the current feature branch, using Python's built-in `unittest` framework:

| Test module | Test methods | Coverage |
| --- | ---: | --- |
| `tests/test_optimizer.py` | 13 | Core calculations, FFD allocation, sorting, decimal precision |
| `tests/test_routes.py` | 23 | HTML forms, persistence, history, CSV, errors and limits |
| `tests/test_api.py` | 15 | Successful JSON requests, structure, lengths, quantities, non-finite values, limits |
| **Total** | **51** | |

Tests use `unittest.mock`, the Flask test client, an in-memory SQLite database, and the Flask application factory pattern. SQLite isolates tests from the local PostgreSQL database; mocks simulate database failures without interrupting a live database.

Run all tests from the project root:

```bash
python -m unittest discover -s tests -v
```

The 15 API tests passed in the latest shared API run. **Run the full suite again locally after updating the branch** to verify the current overall result.

Automated GitHub Actions CI has not yet been configured. SQLite tests do not replace separate PostgreSQL integration testing.

## Running the Project Locally

### Prerequisites

- Python 3.12
- PostgreSQL
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/Monsyerz/cutflow.git
cd cutflow
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows using Git Bash:

```bash
source .venv/Scripts/activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Ensure PostgreSQL is installed and running. Create the database:

```sql
CREATE DATABASE cutflow_db;
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cutflow_db
DB_USER=postgres
DB_PASSWORD=your_postgresql_password
SECRET_KEY=your_generated_secret_key
```

Replace placeholders with your own local PostgreSQL credentials. Generate a secure Flask secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Never commit `.env` files or real database credentials to GitHub.**

### 6. Apply Database Migrations

```bash
python -m flask --app run db upgrade
```

### 7. Run the Application

```bash
python run.py
```

Open the following URLs:

- Optimizer: http://127.0.0.1:5000/
- Optimization history: http://127.0.0.1:5000/history
- CSV export: http://127.0.0.1:5000/export
- REST API: `POST http://127.0.0.1:5000/api/optimize`

## Current Limitations

- Only one stock length is supported per optimization.
- Stock inventory is assumed to be unlimited.
- Cutting blade thickness (*kerf*) is not yet considered.
- The database stores optimization summaries rather than complete cutting layouts.
- The web UI currently visualizes the last stock piece rather than the full allocation.
- The API returns summaries but does not persist requests or results to history.
- Request-body size limits and custom handling of malformed JSON are not yet implemented.
- The application has not yet been publicly deployed.
- The application is not intended for production manufacturing use.

## Development Roadmap

### Completed

- [x] Flask application factory and web interface
- [x] Custom Merge Sort implementation
- [x] First Fit Decreasing optimization algorithm
- [x] Backend numeric and form validation
- [x] Dynamic JavaScript cut inputs
- [x] Form value preservation after validation errors
- [x] PostgreSQL database integration
- [x] SQLAlchemy ORM models
- [x] Flask-Migrate and Alembic migrations
- [x] Database transaction rollback
- [x] Database query failure handling
- [x] Optimization history page
- [x] Display the latest 10 optimization results
- [x] CSV export of all saved optimization results
- [x] CSV export error handling
- [x] Optimization summary and last-stock visualization
- [x] Decimal-based floating-point precision fix
- [x] Regression testing for floating-point errors
- [x] JSON REST API (`POST /api/optimize`)
- [x] REST API request validation, non-finite value checks, and 1,000-cut limit
- [x] 15 automated REST API tests (51 test methods overall)

### Next Steps

- [ ] Implement GitHub Actions CI for automated testing
- [ ] Add stricter request validation and payload-size limits
- [ ] Add PostgreSQL integration tests
- [ ] Improve cutting layout visualization and accessibility
- [ ] Prepare production deployment configuration
- [ ] Deploy Flask application with hosted PostgreSQL
- [ ] Add live application URL and screenshots to README
- [ ] Connect the live project to personal portfolio

### Potential Future Enhancements

- [ ] Save complete cutting layouts and original inputs
- [ ] Support multiple stock lengths
- [ ] Support limited stock inventory
- [ ] Account for cutting blade thickness (kerf)
- [ ] Add project and material management functionality
- [ ] Explore additional optimization strategies
- [ ] Benchmark optimization performance

## Project Status

CutFlow is an actively developed software engineering portfolio project combining algorithm design, backend development, database persistence, REST API design, error handling, and automated testing.

The current application includes a cutting optimizer, web interface, PostgreSQL integration, optimization history, CSV export, and a JSON REST API with 15 dedicated API tests. There are 51 test methods defined across the repository's three test modules.

The project is not intended for production manufacturing use.

## Author

**Kacper Popek**

Software Engineering student interested in backend development, data structures, algorithms, relational databases, and engineering-focused software.

**GitHub:** https://github.com/Monsyerz