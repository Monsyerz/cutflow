# CutFlow

CutFlow is a web-based material cutting optimizer built with Python and Flask.

The goal of the project is to reduce material waste by organizing required cuts across available stock lengths as efficiently as possible.

The project also serves as a practical implementation of sorting algorithms, optimization logic, and Flask backend development.

## Features

- Enter stock length, cut length, and quantity
- Automatically expand requested cuts
- Sort cuts using a custom Merge Sort implementation
- Optimize stock usage using a First Fit Decreasing approach
- Calculate total material waste
- Calculate stock utilization percentage
- Display optimization results directly in the browser
- Basic client-side input validation

## How It Works

CutFlow processes the user's input through the following pipeline:

1. The user enters the stock length, cut length, and quantity.
2. Flask receives the form data.
3. Requested cuts are expanded into individual cut lengths.
4. A custom Merge Sort implementation sorts the cuts from largest to smallest.
5. First Fit Decreasing places each cut into the first available stock where it fits.
6. CutFlow calculates:
   - stock usage
   - remaining waste
   - utilization percentage
7. Results are returned to the frontend using Jinja templates.

## Example

```text
Stock Length: 20
Cut Length: 10.5
Quantity: 1

Result:
Stocks: [[10.5]]
Waste: 9.50
Utilization: 52.50%
```

## Tech Stack

- Python
- Flask
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
│   │   └── styles.css
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

Before optimization, requested cuts are sorted from largest to smallest using a custom Merge Sort implementation.

The optimizer checks existing stock pieces and places each cut into the first stock where enough space remains.

If no existing stock can fit the cut, a new stock piece is created.

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

- Support for multiple different cut lengths in one optimization
- Dynamic cut rows using JavaScript
- Improved optimization result visualization
- Server-side validation
- Automated tests with pytest
- Persistent project data
- Database integration
- Material and project management features

## Project Status

CutFlow is currently under active development.

The initial optimization engine and Flask web interface are functional.

Additional input options, validation, testing, and persistence will be added as the project develops.

## Author

**Kacper Popek**

Software Engineering student building projects focused on Python, backend development, algorithms, and practical problem solving.