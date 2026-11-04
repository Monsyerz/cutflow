
# CutFlow

**Smarter cuts. Less waste.**

CutFlow is a web-based, one-dimensional material cutting optimizer built with **Python, Flask, PostgreSQL, and JavaScript**. It uses the **First Fit Decreasing (FFD)** heuristic, supported by a custom Merge Sort implementation, to arrange required cuts into stock pieces and estimate material waste.

The project combines my background in engineering with software engineering concepts: algorithms, input validation, relational databases, ORM, database migrations, automated testing, and error handling.

> **Status:** Active development. The application currently runs locally; public deployment is planned.
>
> **Latest local test result:** 33 tests passed using Python `unittest`.

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

### Validation and Reliability

- Validate stock lengths, cut lengths, and quantities on the backend, alongside HTML form validation.
- Reject missing, invalid, non-positive, and non-finite length values.
- Reject non-integer or non-positive quantities and mismatched cut/quantity lists.
- Prevent individual cuts from exceeding the stock length.
- Preserve submitted form values after validation errors.
- Roll back failed database writes and display user-friendly error messages.
- Handle database query failures when displaying history or exporting CSV.

### Persistence and History

- Save optimization summaries in PostgreSQL using Flask-SQLAlchemy.
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

1. The user submits a stock length and one or more cut length/quantity pairs.
2. Flask validates the submitted values and preserves form inputs if validation fails.
3. `expand_cuts()` converts quantities into a list of individual cuts.
4. `merge_sort()` sorts the cuts in descending order.
5. `optimize_cuts()` applies **First Fit Decreasing**: each cut is placed in the first existing stock piece with enough capacity; otherwise, a new stock piece is created.
6. `calculate_waste()` and `calculate_utilization()` compute material metrics.
7. SQLAlchemy saves the optimization summary to PostgreSQL. A failed write triggers a session rollback.
8. Jinja2 renders the results; the History page and CSV endpoint expose saved summaries.

### Why Decimal?

Ordinary binary floating-point arithmetic can produce results such as:

```python
0.2 + 0.1 == 0.3  # False
```

That could incorrectly cause an exact-fit combination to occupy two stock pieces or produce a tiny negative waste value.

CutFlow converts numeric inputs to `Decimal` using their string representation during capacity checks and metric calculations, then returns the expected result types to the rest of the application.

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
| Backend | Python, Flask |
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

Currently, the database stores **optimization summaries only**, not full cutting layouts or original input values.

`Decimal` is used during calculations, while the persisted waste and utilization fields remain SQLAlchemy `Float` columns.

### Routes

| Route | Method | Behavior |
| --- | --- | --- |
| `/` | GET | Display the optimizer form |
| `/` | POST | Validate inputs, optimize cuts, save results, and display a summary |
| `/history` | GET | Display the latest 10 saved summaries |
| `/export` | GET | Download all saved summaries as `history.csv` |

The CSV export includes:

- ID
- Stocks Used
- Waste
- Utilization
- Created At

If the export database query fails, the application displays an error response with HTTP **503** instead of returning a CSV download.

## Automated Testing

The project currently has **33 automated test methods**, implemented using Python's built-in `unittest` framework.

### Optimizer Tests — 13

These tests verify:

- Waste calculations
- Utilization calculations
- Quantity expansion
- Merge Sort correctness
- Merge Sort edge cases
- First Fit Decreasing allocation
- Large stock lengths
- Empty inputs
- Exact stock fills
- Separate stock allocation
- Decimal cut lengths
- Input preservation and stock-capacity constraints
- Floating-point precision regression

### Flask Route Tests — 20

These tests verify:

- Home page rendering
- Stock length validation
- Cut length validation
- Quantity validation
- Missing and mismatched inputs
- Form value preservation
- Successful optimization and database persistence
- Database transaction rollback
- Exact stock fills
- Empty optimization history
- History ordering and result limits
- CSV export functionality
- CSV export with an empty database
- CSV data integrity and ordering
- Database failure handling

### Testing Configuration

Tests use:

- Python `unittest`
- `unittest.mock`
- Flask test client
- SQLite in-memory database
- Flask application factory pattern

The SQLite test database provides isolation from the local PostgreSQL database.

`unittest.mock` simulates database failures without interrupting a live PostgreSQL instance.

`subTest()` is used to validate multiple scenarios within individual test methods.

### Running Tests

From the project root, execute:

```bash
python -m unittest discover -s tests -v
```

**Latest locally verified result:**

```text
----------------------------------------------------------------------
Ran 33 tests in 0.289s

OK
```

All 33 automated tests passed locally.

Automated GitHub Actions CI has not yet been configured. The existing SQLite tests do not replace separate integration testing against PostgreSQL.

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

Activate the environment on Windows using Git Bash:

```bash
source .venv/Scripts/activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Ensure PostgreSQL is installed and running.

Create a database:

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

Replace the placeholders with your local PostgreSQL credentials.

Generate a secure Flask secret key:

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

Open the application in your browser:

**Optimizer:**

http://127.0.0.1:5000/

**Optimization History:**

http://127.0.0.1:5000/history

**CSV Export:**

http://127.0.0.1:5000/export

## Current Limitations

- Only one stock length is supported per optimization.
- Stock inventory is assumed to be unlimited.
- Cutting blade thickness (*kerf*) is not yet considered.
- The database stores optimization summaries rather than complete cutting layouts.
- The UI currently visualizes the last stock piece rather than the full allocation.
- Large quantities are not yet limited by a dedicated backend cap.
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
- [x] 33 automated tests using unittest

### Next Steps

- [ ] Implement GitHub Actions CI for automated testing
- [ ] Introduce input-size limits and additional reliability checks
- [ ] Improve cutting layout visualization and accessibility
- [ ] Implement JSON REST API (`POST /api/optimize`)
- [ ] Add automated REST API tests
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

CutFlow is an actively developed software engineering portfolio project combining algorithm design, backend development, database persistence, error handling, and automated testing.

The current application includes a functional cutting optimizer, web interface, PostgreSQL integration, optimization history, CSV export, and 33 locally passing automated tests.

The project is not intended for production manufacturing use.

## Author

**Kacper Popek**

Software Engineering student interested in backend development, data structures, algorithms, relational databases, and engineering-focused software.

**GitHub:** https://github.com/Monsyerz
