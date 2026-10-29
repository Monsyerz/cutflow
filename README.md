# CutFlow

**Smarter cuts. Less waste.**

CutFlow is a web-based material cutting optimizer built with Python, Flask, PostgreSQL, and JavaScript.

The goal of the project is to reduce material waste by organizing required cuts across available stock lengths using a **First Fit Decreasing (FFD)** optimization strategy.

The project demonstrates practical knowledge of data structures and algorithms, backend development, relational databases, object-relational mapping (ORM), database migrations, automated testing, error handling, and frontend integration.

> **Project Status:** Active Development  
> CutFlow is currently a functional local web application. Additional features and public deployment are planned.

## Features

- Enter stock length, cut length, and quantity
- Add and remove multiple cut rows dynamically using JavaScript
- Support multiple different cut lengths in a single optimization
- Perform client-side and backend input validation
- Handle invalid, missing, negative, and non-finite numeric inputs
- Preserve submitted form values after validation errors
- Automatically expand requested cuts based on quantity
- Sort cuts using a custom Merge Sort implementation
- Optimize stock usage using First Fit Decreasing
- Calculate total material waste and utilization percentage
- Calculate total cut length and number of cuts
- Display stock pieces used and a detailed cutting layout
- Automatically save optimization results to PostgreSQL
- Use SQLAlchemy ORM for database operations
- Manage database schema changes with Flask-Migrate and Alembic
- Handle database transaction failures using rollback
- Display the 10 most recent optimizations on a History page
- Navigate between Home, Optimizer, About, and History
- Configure application secrets using environment variables
- Support isolated testing through Flask application configuration
- Run automated tests using Python's built-in unittest framework

## How It Works

CutFlow processes the user's input through the following pipeline:

1. The user enters the available stock length.
2. The user enters the required cut lengths and quantities.
3. JavaScript allows cut rows to be dynamically added or removed.
4. Flask receives and validates the submitted form data.
5. Invalid inputs generate descriptive error messages while preserving submitted values.
6. Requested quantities are expanded into individual cuts.
7. A custom Merge Sort implementation sorts the cuts in descending order.
8. First Fit Decreasing places each cut into the first available stock piece where it fits.
9. CutFlow calculates:
   - Total cuts
   - Total cut length
   - Stock pieces used
   - Remaining material waste
   - Material utilization percentage
10. SQLAlchemy creates an optimization result record and saves it to PostgreSQL.
11. If a database transaction fails, SQLAlchemy rolls back the transaction and Flask displays an error message.
12. Flask renders the optimization summary and cutting layout using Jinja2 templates.
13. The History page displays the 10 most recent saved optimization summaries.

## Example

```text
Stock Length: 20

Cuts:
15 × 2
10.5 × 3
7 × 1
5 × 2

Result:

Total Cuts: 8
Stocks Used: 5
Total Cut Length: 78.50
Waste: 21.50
Utilization: 78.50%

Cutting Layout:

Stock 1: 15 + 5
Stock 2: 15 + 5
Stock 3: 10.5 + 7
Stock 4: 10.5
Stock 5: 10.5
```

## Tech Stack

**Backend**
- Python
- Flask
- SQLAlchemy
- Flask-SQLAlchemy

**Database**
- PostgreSQL
- psycopg
- Flask-Migrate
- Alembic

**Frontend**
- HTML
- CSS
- JavaScript
- Jinja2

**Testing**
- Python unittest
- unittest.mock
- Flask test client
- SQLite in-memory test configuration

**Development Tools**
- Git
- GitHub
- VS Code
- python-dotenv

## Project Structure

```text
cutflow/
│
├── app/
│   ├── static/
│   │   ├── styles.css
│   │   └── script.js
│   │
│   ├── templates/
│   │   ├── index.html
│   │   └── history.html
│   │
│   ├── __init__.py
│   ├── db_models.py
│   ├── extensions.py
│   ├── models.py
│   ├── optimizer.py
│   └── routes.py
│
├── tests/
│   ├── test_optimizer.py
│   └── test_routes.py
│
├── migrations/
│   └── versions/
│
├── .gitignore
├── README.md
├── requirements.txt
└── run.py
```

## Optimization Logic

CutFlow uses the **First Fit Decreasing (FFD)** heuristic to solve a one-dimensional cutting stock problem.

Before optimization, requested cuts are expanded based on their quantities and sorted from largest to smallest using a custom Merge Sort implementation.

The optimizer processes each cut and checks existing stock pieces in order.

If sufficient space remains in an existing stock piece, the cut is assigned to that piece.

If no existing stock piece can accommodate the cut, a new stock piece is created.

First Fit Decreasing does not guarantee a mathematically optimal solution for every input, but it provides an efficient method for generating practical cutting layouts.

### Current Limitations

- The optimizer assumes a single stock length.
- The available stock inventory is treated as unlimited.
- Cutting blade thickness (kerf) is not currently considered.
- Complete cutting layouts and original input data are not yet stored in the database.

## Database Integration

CutFlow uses PostgreSQL to persist optimization summaries.

Flask-SQLAlchemy provides an ORM layer that allows the application to interact with the database through Python objects rather than manually written SQL statements.

### Database Model

The `OptimizationResult` model represents the `optimization_results` table.

| Column | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| stocks_used | Integer | Number of stock pieces used |
| waste | Float | Remaining material waste |
| utilization | Float | Material utilization percentage |
| created_at | DateTime | Timestamp of the optimization |

### Data Persistence

After the optimization algorithm completes, Flask creates an `OptimizationResult` object containing the calculated metrics.

SQLAlchemy adds the object to a database session and commits the transaction.

This allows optimization summaries to be saved automatically whenever a successful optimization is submitted.

The current implementation stores summary metrics rather than complete cutting layouts or original input data.

### Database Transaction Error Handling

CutFlow uses SQLAlchemy exception handling to manage database transaction failures.

Database write operations are wrapped in a `try/except` block.

If SQLAlchemy raises a database exception during the operation, the application calls:

```python
db.session.rollback()
```

This rolls back the current uncommitted transaction and allows the application to recover from a failed database write.

The user receives a generic error message instead of internal database exception details.

Database error handling currently covers optimization result writes. Additional error handling for history queries is planned.

### Optimization History

CutFlow includes an optimization history page accessible through `/history`.

The page retrieves the 10 most recent optimization records from PostgreSQL.

Results are ordered by their creation date, with the newest records displayed first.

Each record displays:

- Optimization ID
- Number of stock pieces used
- Total material waste
- Material utilization percentage
- Date of optimization

The 10-record limit only controls how many results are displayed. Older optimization records remain stored in PostgreSQL.

### Database Migrations

CutFlow uses Flask-Migrate and Alembic to manage database schema changes.

Migrations allow database tables and columns to be introduced or modified without manually recreating the database structure.

The initial migration creates the `optimization_results` table.

## Input Validation & Error Handling

CutFlow performs frontend and backend validation before processing optimization requests.

### Backend Validation

The application checks that:

- Stock length is a valid, positive, finite number
- Cut lengths are valid, positive, finite numbers
- Cut lengths do not exceed the available stock length
- Quantities are positive integers
- Every submitted cut length has a corresponding quantity
- At least one cut is provided
- Invalid numeric strings are rejected
- Missing or empty required values are rejected

Python's `try/except` blocks handle invalid numeric conversions.

The `math.isfinite()` function prevents non-finite values such as `NaN` and infinity from being accepted as stock or cut lengths.

### Frontend Validation

HTML input restrictions provide additional client-side validation using attributes such as:

- `type="number"`
- `required`
- `min`
- `step`

Backend validation remains responsible for verifying submitted data, even if frontend restrictions are bypassed.

### Form Value Persistence

CutFlow preserves previously submitted values when validation fails.

Jinja2 retrieves the submitted stock length using `request.form.get()`.

Dynamic cut lengths and quantities are retrieved using `request.form.getlist()`.

A Jinja2 loop reconstructs the submitted cut rows and restores their values.

This allows users to correct invalid entries without re-entering the entire form.

JavaScript supports removing restored dynamic cut rows.

## Automated Testing

CutFlow uses Python's built-in `unittest` framework to verify optimization functions and Flask route behavior.

The current automated test suite contains **10 tests**.

### Optimization Algorithm Tests

**1. `test_calculate_utilization()`**
- Verifies material utilization calculations.
- Compares the result against an expected percentage.

**2. `test_calculate_waste()`**
- Verifies total material waste calculations.
- Checks unused material across stock pieces.

**3. `test_expand_cuts()`**
- Verifies that quantities are expanded into individual cuts.
- Compares the expanded list against expected values.

**4. `test_merge_sort()`**
- Verifies that Merge Sort orders cuts in descending order.
- Confirms the output matches the expected sequence.

### Flask Route & Validation Tests

**5. `test_database_rollback()`**
- Simulates a failed database commit using `unittest.mock`.
- Verifies that `rollback()` is called.
- Checks that the application returns an error message.

**6. `test_empty_cuts()`**
- Submits an optimization request without cut entries.
- Verifies that the application rejects the empty cut list.

**7. `test_invalid_cut_length()`**
- Submits a non-numeric cut length.
- Verifies the expected validation message.

**8. `test_negative_cut_length()`**
- Submits a negative cut length.
- Verifies rejection of negative values.
- Checks that the previously submitted stock length is preserved.

**9. `test_cut_length_exceeds_stock_length()`**
- Submits a cut length greater than the stock length.
- Verifies that the application rejects the input.

**10. `test_preserve_cut_values()`**
- Submits multiple cut lengths and quantities.
- Triggers a validation error.
- Verifies that previously submitted values remain in the HTML response.

### Testing Configuration

CutFlow uses the Flask Application Factory Pattern.

The `create_app()` function accepts an optional test configuration.

This allows tests to use an isolated SQLite in-memory database configuration instead of the local PostgreSQL database.

Flask's test client sends simulated HTTP requests without starting a development server.

`unittest.mock` allows database failures to be simulated without intentionally interrupting PostgreSQL.

The rollback test verifies application behavior using mocks rather than testing actual PostgreSQL transaction recovery.

### Running Tests

From the project root, run:

```bash
python -m unittest discover -s tests -v
```

Latest verified local test result:

```text
Ran 10 tests in 0.195s

OK
```

All 10 automated tests passed.

Additional test coverage for database read failures, invalid quantities, unusual inputs, and frontend interactions is planned.

## Application Configuration & Security

CutFlow uses environment variables to keep sensitive configuration values outside the source code.

The application loads environment variables using `python-dotenv`.

The Flask `SECRET_KEY` and PostgreSQL connection credentials are stored in a local `.env` file.

The `.env` file is excluded from version control through `.gitignore`.

The Flask secret key is used to cryptographically sign session data and protect its integrity when Flask session features are used.

A separate test configuration allows automated tests to run without requiring production database credentials or the application's real secret key.

For production deployment, environment variables and secrets will be configured through the hosting provider rather than committed to the repository.

## Running the Project

### Prerequisites

- Python 3.12 or compatible version
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

Activate the environment using Windows Git Bash:

```bash
source .venv/Scripts/activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Ensure PostgreSQL is installed and running.

Connect to PostgreSQL and create the application database:

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

Replace the placeholders with your local PostgreSQL credentials and a randomly generated secret key.

Generate a secure Flask secret key using:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Do not commit the `.env` file or share real database credentials and secret keys.

The `.gitignore` file excludes local environment files and Python-generated artifacts.

A dedicated database user with limited permissions is recommended for production deployments.

### 6. Apply Database Migrations

Run:

```bash
python -m flask --app run db upgrade
```

This applies the existing migrations and creates the required database tables.

To check the current migration revision:

```bash
flask db current
```

### 7. Run the Application

```bash
python run.py
```

Open the application in your browser:

```text
http://127.0.0.1:5000/
```

Optimization History:

```text
http://127.0.0.1:5000/history
```

The application currently runs using Flask's development server and a local PostgreSQL database.

## Development Roadmap

CutFlow is being developed incrementally, with a focus on reliability, maintainability, and practical functionality.

The development phases are organized in the following order:

**Validation & Error Handling → CSV Export → Visualization → REST API → Deployment**

### Completed

- [x] Custom Merge Sort implementation
- [x] First Fit Decreasing optimization algorithm
- [x] Flask web application
- [x] Dynamic JavaScript input rows
- [x] Text-based cutting layout
- [x] Material waste and utilization calculations
- [x] PostgreSQL database integration
- [x] SQLAlchemy ORM models
- [x] Alembic database migrations
- [x] Automatic optimization result persistence
- [x] Optimization History page
- [x] Display the 10 most recent optimization results
- [x] Basic navigation and About section
- [x] Flask application factory with configurable test settings
- [x] Environment-based Flask secret key configuration
- [x] 10 automated tests using unittest

### Phase 1 — Improved Validation & Error Handling (Mostly Completed)

**Goal:** Improve application reliability and prevent unexpected server errors.

- [x] Implement try/except handling for invalid numeric input
- [x] Handle empty or missing form values
- [x] Reject non-finite stock and cut lengths
- [x] Improve validation error messages displayed to users
- [x] Implement database transaction rollback handling
- [x] Handle optimization result commit failures
- [x] Add tests for invalid input and edge cases
- [x] Preserve submitted stock length after validation errors
- [x] Preserve dynamically submitted cut lengths and quantities
- [x] Simulate database commit failures using unittest.mock
- [ ] Add graceful handling for database read failures on the History page
- [ ] Expand tests for invalid quantities and additional edge cases
- [ ] Add further frontend interaction tests

### Phase 2 — CSV Export (Next)

**Goal:** Allow users to download optimization results for external use.

- [ ] Implement CSV file generation
- [ ] Add a Download CSV button
- [ ] Export optimization summary data
- [ ] Include meaningful column headers
- [ ] Format numerical values consistently
- [ ] Validate exported results through automated tests

### Phase 3 — Visual Cutting Layout

**Goal:** Improve how optimization results are presented.

- [ ] Create graphical representations of stock pieces
- [ ] Display individual cuts as proportional segments
- [ ] Visually distinguish used material from remaining waste
- [ ] Display material utilization percentages
- [ ] Improve responsive layout for smaller screens
- [ ] Improve accessibility and visual clarity

### Phase 4 — REST API

**Goal:** Allow external applications to access the CutFlow optimization engine.

- [ ] Create a REST API endpoint such as `POST /api/optimize`
- [ ] Accept optimization inputs in JSON format
- [ ] Return optimization results as JSON
- [ ] Provide meaningful API validation errors
- [ ] Reuse the existing optimization algorithms
- [ ] Implement API endpoint tests
- [ ] Document API requests and responses

The REST API will allow other applications and scripts to interact with the CutFlow optimization engine without using the HTML interface.

### Phase 5 — Deployment

**Goal:** Make CutFlow publicly accessible.

- [ ] Prepare production configuration
- [ ] Configure secure environment variables
- [ ] Set up a production WSGI server
- [ ] Configure a hosted PostgreSQL database
- [ ] Apply database migrations in production
- [ ] Deploy the application to a hosting platform
- [ ] Test the deployed application
- [ ] Add the live application URL to the README
- [ ] Connect the deployed application to the personal portfolio

### Potential Future Enhancements

- [ ] Store complete cutting layouts and original input data
- [ ] Support multiple stock lengths
- [ ] Support limited material inventory
- [ ] Include cutting blade thickness (kerf)
- [ ] Add material and project management functionality
- [ ] Expand automated test coverage

## Project Status

CutFlow is currently under active development.

The application includes a functional optimization engine, Flask web interface, dynamic JavaScript inputs, cutting layout display, and PostgreSQL integration.

Optimization summaries are automatically saved using SQLAlchemy ORM, and database schema changes are managed through Alembic migrations.

The application includes an Optimization History page, improved backend validation, database rollback handling, form value preservation, and 10 passing automated tests.

The next development phase will focus on CSV export functionality, alongside additional reliability improvements.

CutFlow is currently a portfolio project and is not intended for production manufacturing use.

Feedback and suggestions are welcome through the project's GitHub repository.

## Author

**Kacper Popek**

Software Engineering student focused on Python, backend development, data structures, algorithms, relational databases, and practical software engineering solutions.

**GitHub:** https://github.com/Monsyerz