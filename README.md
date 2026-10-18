# CutFlow

CutFlow is a web-based material cutting optimizer built with Python, Flask, PostgreSQL, and JavaScript.

The goal of the project is to reduce material waste by organizing required cuts across available stock lengths using a **First Fit Decreasing (FFD)** optimization strategy.

The project demonstrates practical knowledge of data structures and algorithms, backend development, relational databases, object-relational mapping (ORM), database migrations, and frontend integration.

## Features

- Enter stock length, cut length, and quantity
- Add and remove multiple cut rows dynamically using JavaScript
- Support multiple cut lengths in a single optimization
- Validate stock length, cut lengths, and quantities on the backend
- Automatically expand requested cuts based on quantity
- Sort cuts using a custom Merge Sort implementation
- Optimize stock usage using First Fit Decreasing
- Calculate total material waste and utilization percentage
- Calculate total cut length and number of cuts
- Display stock pieces used and a detailed cutting layout
- Provide basic client-side input validation
- Automatically save optimization results to PostgreSQL
- Use SQLAlchemy ORM for database operations
- Manage database schema changes with Flask-Migrate and Alembic

## How It Works

CutFlow processes user input through the following pipeline:

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
│   │   └── index.html
│   │
│   ├── __init__.py
│   ├── db_models.py
│   ├── extensions.py
│   ├── models.py
│   ├── optimizer.py
│   └── routes.py
│
├── migrations/
│   ├── versions/
│   ├── alembic.ini
│   └── env.py
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

The current implementation assumes a single stock length and does not account for cutting blade thickness (kerf) or limited stock inventory.

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

### Database Migrations

CutFlow uses Flask-Migrate and Alembic to manage database schema changes.

Migrations allow database tables and columns to be introduced or modified without manually recreating the database structure.

The initial migration creates the `optimization_results` table.

## Input Validation

CutFlow performs backend validation before processing an optimization.

The application checks that:

- Stock length is greater than zero
- Cut lengths are greater than zero
- Cut lengths do not exceed stock length
- Quantities are positive integers
- Every submitted cut length has a corresponding quantity

HTML input restrictions also provide basic client-side validation.

Additional handling for malformed numeric input and database failures is planned.

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

The application currently runs using Flask's development server and a local PostgreSQL database.

## Roadmap

### Completed

- [x] Custom Merge Sort implementation
- [x] First Fit Decreasing optimization algorithm
- [x] Flask web application
- [x] Dynamic JavaScript input rows
- [x] Cutting layout visualization
- [x] Material waste and utilization calculations
- [x] Backend input validation
- [x] PostgreSQL database integration
- [x] SQLAlchemy ORM models
- [x] Alembic database migrations
- [x] Automatic optimization result persistence

### Planned

- [ ] Improved backend validation and error handling
- [ ] Database transaction rollback handling
- [ ] Automated unit tests using pytest
- [ ] Additional algorithm edge-case testing
- [ ] Optimization history page
- [ ] Save complete cutting layouts and original input data
- [ ] Visual stock utilization diagrams
- [ ] Preserve input values after optimization
- [ ] Material and project management features
- [ ] Improved responsive UI
- [ ] Production deployment configuration

## Project Status

CutFlow is currently under active development.

The application includes a functional optimization engine, Flask web interface, dynamic JavaScript inputs, cutting layout visualization, and PostgreSQL database integration.

Optimization results are automatically persisted using SQLAlchemy ORM, and database schema changes are managed with Alembic migrations.

The next development phase will focus on improving reliability, implementing automated tests, and developing an optimization history feature.

## Author

**Kacper Popek**

Software Engineering student focused on Python, backend development, data structures, algorithms, relational databases, and practical software engineering solutions.