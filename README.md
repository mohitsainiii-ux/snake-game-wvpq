# Student Performance Analysis System

A small, beginner-friendly Python project that uses **Pandas** to load and
analyse student records and **NumPy** for numerical statistics. It demonstrates
CSV loading, cleaning, filtering, grouping, sorting, aggregation, and
relationship checks using a realistic sample dataset.

## Requirements and setup

Python 3.9 or newer is recommended. From the repository root, create an
environment and install the only two dependencies:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run the analysis with:

```bash
python student_analysis.py
```

The script builds its CSV path from its own location, so it also works when
launched from a different current directory.

## Folder structure

```text
.
├── data/
│   └── students.csv       # Sample input, including data-quality problems
├── student_analysis.py    # Load, clean, calculate, and display the report
├── requirements.txt       # Pandas and NumPy
└── README.md
```

## Cleaning behavior

The sample intentionally includes a blank name, text in a numeric column,
missing marks, a negative mark, a mark above 100, and out-of-range attendance.
The script:

1. Strips text fields and removes rows without a usable Student ID, Name, or
   Class, because those records cannot be identified reliably.
2. Coerces numeric columns with `errors="coerce"`; non-numeric text becomes
   missing.
3. Converts marks, attendance, age, and study hours outside sensible ranges to
   missing values instead of accepting them.
4. Fills missing/invalid numeric values with that column's median. Median
   imputation is simple and less sensitive to extreme values than a mean.
5. Labels missing gender as `Unknown`.

The report prints how many rows were removed and how many numeric values were
filled, making the cleaning decisions visible.

## Outputs

Running the script displays:

- Each cleaned student's total marks, average, letter grade, and pass/fail
- NumPy mean, median, standard deviation, minimum, maximum, and percentiles
- Class-wise and subject-wise averages
- The top 10 students sorted by average and total marks
- Average performance in attendance bands
- Average performance in study-hour bands and a NumPy correlation

The pass rule is at least 40 marks in every subject. Grades are based on the
average: A+ (90+), A (80+), B (70+), C (60+), D (50+), E (40+), and F below
40.
