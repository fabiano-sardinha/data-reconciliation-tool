from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import FormulaRule


def create_excel_report(result_df, output_file):

    # Create the output folder if it does not exist yet
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    # Replace missing values with empty cells
    result_df = result_df.fillna("")

    # Save the report to Excel
    result_df.to_excel(output_file, index=False)

    # Open the generated file to apply formatting
    workbook = load_workbook(output_file)
    worksheet = workbook.active

    # Header formatting
    for cell in worksheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    # Freeze the first row
    worksheet.freeze_panes = "A2"

    # Enable filters
    worksheet.auto_filter.ref = worksheet.dimensions

    # Adjust column widths
    column_widths = {
        "A": 14,
        "B": 20,
        "C": 20,
        "D": 28,
        "E": 28,
        "F": 12,
        "G": 12,
        "H": 14,
        "I": 60,
        "J": 18
    }

    for column, width in column_widths.items():
        worksheet.column_dimensions[column].width = width

    # Align the data
    for row in worksheet.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="center")

    # Conditional formatting for the Status column
    status_colors = {
        "MATCHED": "C6EFCE",
        "CHANGED": "FFEB9C",
        "MISSING": "FFC7CE",
        "NEW": "BDD7EE",
        "DUPLICATE": "F4CCCC"
    }

    for status, color in status_colors.items():

        fill = PatternFill(
            start_color=color,
            end_color=color,
            fill_type="solid"
        )

        worksheet.conditional_formatting.add(
            f"H2:H{worksheet.max_row}",
            FormulaRule(
                formula=[f'H2="{status}"'],
                fill=fill
            )
        )

    # Save again
    workbook.save(output_file)

    print(f"\nReport created successfully: {output_file}")
