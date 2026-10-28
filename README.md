
# CutFlow

**Smarter cuts. Less waste.**

CutFlow is a web-based material cutting optimizer built with Python, Flask, PostgreSQL, and JavaScript.

The goal of the project is to reduce material waste by organizing required cuts across available stock lengths using a **First Fit Decreasing (FFD)** optimization strategy.

The project demonstrates practical knowledge of data structures and algorithms, backend development, relational databases, object-relational mapping (ORM), database migrations, automated testing, and frontend integration.

> **Project Status:** Active Development  
> CutFlow is currently a functional local web application. Additional features and public deployment are planned.

## Features

- Enter stock length, cut length, and quantity
- Add and remove multiple cut rows dynamically using JavaScript
- Support multiple different cut lengths in a single optimization
- Perform basic client-side and backend input validation
- Automatically expand requested cuts based on quantity
- Sort cuts using a custom Merge Sort implementation
- Optimize stock usage using First Fit Decreasing
- Calculate total material waste and utilization percentage
- Calculate total cut length and number of cuts
- Display stock pieces used and a detailed cutting layout
- Automatically save optimization results to PostgreSQL
- Use SQLAlchemy ORM for database operations
- Manage database schema changes with Flask-Migrate and Alembic
- Display the 10 most recent optimizations on a History page
- Navigate between Home, Optimizer, About, and History
- Run automated unit tests using Python's built-in unittest framework

## How It Works

CutFlow processes the user's input through the following pipeline:

1. The user enters the available stock length.
2. The user enters the required cut lengths and quantities.
3. JavaScript allows cut rows to be dynamically added or removed.
4. Flask receives and validates the submitted form data.
5. Requested quantities are expanded into individual cuts.
6. A custom Merge Sort implementation sorts the cuts in descending order.
7. First Fit Decreasing places each cut into the first available stock piece where it fits.
8. CutFlow calculates:
   - Total cuts
   - Total cut length
   - Stock pieces used
   - Remaining material waste
   - Material utilization percentage
9. SQLAlchemy creates an optimization result record and saves it to PostgreSQL.
10. Flask renders the optimization summary and cutting layout using Jinja2 templates.
11. The History page allows users to view the 10 most recent saved optimization summaries.

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
│   └── test_optimizer.py
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

## Input Validation

CutFlow currently performs basic backend validation before processing an optimization.

The application checks that:

- Stock length is greater than zero
- Cut lengths are greater than zero
- Cut lengths do not exceed stock length
- Quantities are positive integers after conversion
- Every submitted cut length has a corresponding quantity

HTML input restrictions also provide basic client-side validation.

Additional error handling for malformed numeric inputs, empty submissions, and database failures is planned.

## Automated Testing

CutFlow uses Python's built-in `unittest` framework to verify the behavior of individual optimization functions.

The current test suite includes four unit tests.

### Implemented Tests

**1. calculate_utilization()**
- Verifies that material utilization is calculated correctly.
- Compares the returned percentage against an expected value.

**2. calculate_waste()**
- Verifies that total material waste is calculated correctly.
- Checks the remaining unused material across stock pieces.

**3. expand_cuts()**
- Verifies that cut quantities are correctly expanded into individual lengths.
- Checks the resulting list against the expected values.

**4. merge_sort()**
- Verifies that the custom Merge Sort algorithm sorts cuts in descending order.
- Confirms that the output matches the expected sequence.

### Running Tests

From the project root, run:

```bash
python -m unittest discover -s tests -v
```

The existing four unit tests have been executed successfully.

Additional test coverage, including edge cases, invalid inputs, and database error handling, is planned.

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
```

Replace the placeholder with your local PostgreSQL password.

The `.env` file is excluded from Git through `.gitignore` to prevent database credentials from being committed to the repository.

A dedicated database user with limited permissions is recommended for production deployments.

### 6. Apply Database Migrations

Run:

```bash
python -m flask --app run db upgrade
```

This applies the existing migrations and creates the required database tables.

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

The next development phases are organized in the following order:

**Validation & Error Handling → CSV Export → Visualization → REST API → Deployment**

### Completed

- [x] Custom Merge Sort implementation
- [x] First Fit Decreasing optimization algorithm
- [x] Flask web application
- [x] Dynamic JavaScript input rows
- [x] Text-based cutting layout
- [x] Material waste and utilization calculations
- [x] Basic backend input validation
- [x] PostgreSQL database integration
- [x] SQLAlchemy ORM models
- [x] Alembic database migrations
- [x] Automatic optimization result persistence
- [x] Optimization History page
- [x] Display the 10 most recent optimization results
- [x] Four automated unit tests using unittest
- [x] Basic navigation and About section

### Phase 1 — Improved Validation & Error Handling (Next)

**Goal:** Improve application reliability and prevent unexpected server errors.

- [ ] Implement try/except handling for invalid numeric input
- [ ] Handle empty or missing form values
- [ ] Reject non-finite numeric values
- [ ] Improve error messages displayed to users
- [ ] Implement database transaction rollback handling
- [ ] Handle database connection and commit failures
- [ ] Add tests for invalid input and edge cases
- [ ] Preserve submitted values when validation fails

### Phase 2 — CSV Export

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

The application also includes an Optimization History page and four automated unit tests.

The next development phase will focus on improving input validation, error handling, and application reliability before implementing additional user-facing functionality.

CutFlow is currently a portfolio project and is not intended for production manufacturing use.

Feedback and suggestions are welcome through the project's GitHub repository.

## Author

**Kacper Popek**

Software Engineering student focused on Python, backend development, data structures, algorithms, relational databases, and practical software engineering solutions.

**GitHub:** https://github.com/Monsyerz

