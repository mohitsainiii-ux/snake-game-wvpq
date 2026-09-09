"""Beginner-friendly student performance analysis using Pandas and NumPy."""

from pathlib import Path

import numpy as np
import pandas as pd


DATA_FILE = Path(__file__).resolve().parent / "data" / "students.csv"
MARK_COLUMNS = ["Math Marks", "Science Marks", "English Marks"]
NUMERIC_COLUMNS = ["Age", *MARK_COLUMNS, "Attendance Percentage", "Study Hours"]


def load_data(file_path=DATA_FILE):
    """Load the CSV using a path relative to this script, not the current shell."""
    return pd.read_csv(file_path)


def clean_data(raw_data):
    """Clean types and impossible values, then fill numeric gaps with medians.

    Invalid numeric values are treated as missing rather than silently accepted.
    The median is used because it is less affected by unusually high or low marks.
    Rows without a usable student ID, name, or class cannot be identified reliably,
    so they are removed.
    """
    data = raw_data.copy()
    original_rows = len(data)

    for column in ["Student ID", "Name", "Gender", "Class"]:
        data[column] = data[column].astype("string").str.strip()

    required_columns = ["Student ID", "Name", "Class"]
    data = data.dropna(subset=required_columns)
    data = data[(data["Student ID"] != "") & (data["Name"] != "") & (data["Class"] != "")]

    # errors="coerce" turns values such as "not available" into NaN.
    for column in NUMERIC_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    valid_ranges = {
        "Age": (10, 25),
        "Attendance Percentage": (0, 100),
        "Study Hours": (0, 24),
    }
    for column in MARK_COLUMNS:
        data.loc[~data[column].between(0, 100), column] = np.nan
    for column, (minimum, maximum) in valid_ranges.items():
        data.loc[~data[column].between(minimum, maximum), column] = np.nan

    missing_before_fill = data[NUMERIC_COLUMNS].isna().sum().sum()
    for column in NUMERIC_COLUMNS:
        data[column] = data[column].fillna(data[column].median())

    data["Gender"] = data["Gender"].fillna("Unknown").replace("", "Unknown")
    data[NUMERIC_COLUMNS] = data[NUMERIC_COLUMNS].round(2)
    data.attrs["rows_removed"] = original_rows - len(data)
    data.attrs["numeric_values_filled"] = int(missing_before_fill)
    return data


def add_performance_metrics(data):
    """Add totals, averages, letter grades, and a pass/fail result."""
    result = data.copy()
    result["Total Marks"] = result[MARK_COLUMNS].sum(axis=1)
    result["Average Marks"] = result[MARK_COLUMNS].mean(axis=1).round(2)

    result["Grade"] = np.select(
        [
            result["Average Marks"] >= 90,
            result["Average Marks"] >= 80,
            result["Average Marks"] >= 70,
            result["Average Marks"] >= 60,
            result["Average Marks"] >= 50,
            result["Average Marks"] >= 40,
        ],
        ["A+", "A", "B", "C", "D", "E"],
        default="F",
    )
    result["Result"] = np.where((result[MARK_COLUMNS] >= 40).all(axis=1), "Pass", "Fail")
    return result


def descriptive_statistics(data):
    """Calculate requested NumPy statistics for the average marks."""
    averages = data["Average Marks"].to_numpy()
    return {
        "Mean": np.mean(averages),
        "Median": np.median(averages),
        "Standard deviation": np.std(averages),
        "Minimum": np.min(averages),
        "Maximum": np.max(averages),
        "25th percentile": np.percentile(averages, 25),
        "75th percentile": np.percentile(averages, 75),
    }


def build_reports(data):
    """Build tables with common Pandas filtering, grouping, sorting, and aggregation."""
    class_average = (
        data.groupby("Class", as_index=False)["Average Marks"]
        .mean()
        .rename(columns={"Average Marks": "Class Average"})
        .sort_values("Class")
    )
    subject_average = (
        data[MARK_COLUMNS].mean().rename("Average Marks").reset_index()
        .rename(columns={"index": "Subject"})
    )
    top_10 = data.sort_values(["Average Marks", "Total Marks"], ascending=False).head(10)

    attendance_bins = [0, 60, 75, 90, 100]
    attendance_labels = ["0-60%", "61-75%", "76-90%", "91-100%"]
    attendance_data = data.assign(
        **{"Attendance Band": pd.cut(
            data["Attendance Percentage"],
            bins=attendance_bins,
            labels=attendance_labels,
            include_lowest=True,
        )}
    )
    attendance_performance = (
        attendance_data.groupby("Attendance Band", observed=False)["Average Marks"]
        .agg(["count", "mean"])
        .reset_index()
        .rename(columns={"mean": "Average Marks"})
    )

    study_bins = [-np.inf, 5, 10, np.inf]
    study_labels = ["0-5 hours", "6-10 hours", "More than 10 hours"]
    study_data = data.assign(
        **{"Study Hours Band": pd.cut(
            data["Study Hours"], bins=study_bins, labels=study_labels
        )}
    )
    study_performance = (
        study_data.groupby("Study Hours Band", observed=False)["Average Marks"]
        .agg(["count", "mean"])
        .reset_index()
        .rename(columns={"mean": "Average Marks"})
    )
    correlation = np.corrcoef(
        data["Study Hours"].to_numpy(), data["Average Marks"].to_numpy()
    )[0, 1]
    return {
        "class_average": class_average,
        "subject_average": subject_average,
        "top_10": top_10,
        "attendance_performance": attendance_performance,
        "study_performance": study_performance,
        "study_correlation": correlation,
    }


def print_report(data, reports):
    """Print the analysis in readable sections for a beginner running the script."""
    print("STUDENT PERFORMANCE ANALYSIS")
    print("=" * 80)
    print(
        f"Students analysed: {len(data)} | "
        f"Rows removed: {data.attrs.get('rows_removed', 0)} | "
        f"Invalid/missing numeric values filled: "
        f"{data.attrs.get('numeric_values_filled', 0)}"
    )
    print("\nCLEANED STUDENT RESULTS")
    print(
        data[
            ["Student ID", "Name", "Class", "Total Marks", "Average Marks", "Grade", "Result"]
        ].to_string(index=False)
    )

    print("\nNUMPY STATISTICS FOR AVERAGE MARKS")
    for name, value in descriptive_statistics(data).items():
        print(f"{name:22}: {value:.2f}")

    print("\nCLASS-WISE AVERAGE")
    print(reports["class_average"].to_string(index=False, formatters={"Class Average": "{:.2f}".format}))
    print("\nSUBJECT-WISE AVERAGE")
    print(reports["subject_average"].to_string(index=False, formatters={"Average Marks": "{:.2f}".format}))
    print("\nTOP 10 STUDENTS")
    print(
        reports["top_10"][["Student ID", "Name", "Average Marks", "Grade"]]
        .to_string(index=False)
    )
    print("\nATTENDANCE VS PERFORMANCE")
    print(reports["attendance_performance"].to_string(index=False, formatters={"Average Marks": "{:.2f}".format}))
    print("\nSTUDY HOURS VS MARKS")
    print(reports["study_performance"].to_string(index=False, formatters={"Average Marks": "{:.2f}".format}))
    print(f"Correlation (study hours and average marks): {reports['study_correlation']:.2f}")


def main():
    """Run the complete load, clean, calculate, and display workflow."""
    cleaned = clean_data(load_data())
    analysed = add_performance_metrics(cleaned)
    print_report(analysed, build_reports(analysed))


if __name__ == "__main__":
    main()
