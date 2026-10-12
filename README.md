# CutFlow

CutFlow is a web-based material cutting optimizer built with Python, Flask, and JavaScript.

The goal of the project is to reduce material waste by organizing required cuts across available stock lengths using a First Fit Decreasing optimization strategy.

The project also serves as a practical implementation of sorting algorithms, optimization logic, backend validation, dynamic frontend behavior, and Flask web development.

## Features

- Enter stock length, cut length, and quantity
- Add and remove multiple cut rows dynamically with JavaScript
- Support multiple different cut lengths in a single optimization
- Validate stock length, cut lengths, and quantities on the backend
- Automatically expand requested cuts based on quantity
- Sort cuts using a custom Merge Sort implementation
- Optimize stock usage using a First Fit Decreasing approach
- Calculate total material waste
- Calculate stock utilization percentage
- Calculate total cut length
- Display total number of cuts
- Display number of stock pieces used
- Display a readable cutting layout for each stock piece
- Basic client-side input validation

## How It Works

CutFlow processes the user's input through the following pipeline:

1. The user enters the available stock length.
2. The user enters one or more cut lengths and quantities.
3. JavaScript allows additional cut rows to be dynamically added or removed.
4. Flask receives the submitted form data.
5. The backend validates stock length, cut lengths, and quantities.
6. Requested quantities are expanded into individual cut lengths.
7. A custom Merge Sort implementation sorts the cuts from largest to smallest.
8. First Fit Decreasing places each cut into the first available stock piece where it fits.
9. CutFlow calculates:
   - total cuts
   - total cut length
   - stock pieces used
   - remaining waste
   - utilization percentage
10. Results and the cutting layout are returned to the frontend using Jinja templates.

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

- Python
- Flask
- JavaScript
- HTML
- CSS
- Jinja2
- Git
- GitHub

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
│   ├── models.py
│   ├── optimizer.py
│   └── routes.py
│
├── .gitignore
├── README.md
├── requirements.txt
└── run.py
```

## Optimization Logic

CutFlow currently uses a First Fit Decreasing strategy.

Before optimization, requested cuts are expanded based on quantity and sorted from largest to smallest using a custom Merge Sort implementation.

The optimizer processes each cut and checks the existing stock pieces in order.

If enough space remains in an existing stock piece, the cut is placed there.

If no existing stock piece can fit the cut, a new stock piece is created.

First Fit Decreasing is a heuristic approach, so it does not guarantee the mathematically optimal solution for every possible cutting problem, but it provides an efficient way to generate practical cutting layouts.

## Input Validation

CutFlow performs validation before running the optimization process.

The application checks that:

- Stock length is greater than zero
- Cut lengths are greater than zero
- Cut lengths do not exceed the stock length
- Quantities are positive integers
- Every submitted cut length has a corresponding quantity

HTML input restrictions also provide basic client-side validation before the form is submitted.

## Running the Project

Clone the repository:

```bash
git clone https://github.com/Monsyerz/cutflow.git
cd cutflow
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment using Windows Git Bash:

```bash
source .venv/Scripts/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python run.py
```

Then open:

```text
http://127.0.0.1:5000/
```

## Roadmap

Planned improvements include:

- Visual stock utilization diagrams
- Improved responsive UI and result presentation
- Preserve form values after optimization
- Automated tests with pytest
- Additional optimizer edge-case testing
- Persistent project data
- Database integration
- Material and project management features

## Project Status

CutFlow is currently under active development.

The optimization engine, Flask web interface, dynamic JavaScript cut inputs, backend validation, optimization summary metrics, and cutting layout display are functional.

The next development phase will focus on result visualization, automated testing, and improving the overall user experience.

## Author

**Kacper Popek**

Software Engineering student building projects focused on Python, backend development, algorithms, and practical problem solving.