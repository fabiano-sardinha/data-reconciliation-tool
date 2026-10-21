import tkinter as tk
from pathlib import Path
import pytest

from gui import ReconciliationApp, DEFAULT_OUTPUT_FILE


@pytest.fixture
def tk_app(monkeypatch):
    monkeypatch.setattr("tkinter.messagebox.showerror", lambda *args, **kwargs: None)
    monkeypatch.setattr("tkinter.messagebox.showwarning", lambda *args, **kwargs: None)
    root = tk.Tk()
    root.withdraw()
    app = ReconciliationApp(root)
    yield app
    try:
        root.destroy()
    except Exception:
        pass


def test_gui_initialization_defaults(tk_app):
    assert tk_app.output_var.get() == DEFAULT_OUTPUT_FILE
    assert tk_app.file_a_var.get() == ""
    assert tk_app.file_b_var.get() == ""
    assert tk_app.status_var.get() == "Select File A and File B to begin."

    for status in ("MATCHED", "CHANGED", "MISSING", "NEW", "DUPLICATE"):
        assert tk_app.metric_vars[status].get() == "-"

    assert str(tk_app.btn_open_report["state"]) == "disabled"
    assert str(tk_app.btn_open_folder["state"]) == "disabled"


def test_gui_on_success_updates_metrics_and_buttons(tk_app, tmp_path):
    report_path = tmp_path / "test_report.xlsx"
    report_path.write_text("fake excel")

    summary = {
        "MATCHED": 10,
        "CHANGED": 3,
        "MISSING": 2,
        "NEW": 1,
        "DUPLICATE": 4,
        "TOTAL": 20,
    }

    tk_app._on_success(summary, str(report_path))

    assert tk_app.metric_vars["MATCHED"].get() == "10"
    assert tk_app.metric_vars["CHANGED"].get() == "3"
    assert tk_app.metric_vars["MISSING"].get() == "2"
    assert tk_app.metric_vars["NEW"].get() == "1"
    assert tk_app.metric_vars["DUPLICATE"].get() == "4"
    assert "20" in tk_app.total_records_var.get()
    assert "completed successfully" in tk_app.status_var.get()

    assert str(tk_app.btn_open_report["state"]) == "normal"
    assert str(tk_app.btn_open_folder["state"]) == "normal"


def test_gui_resets_previous_metrics_on_subsequent_failed_run(tk_app, tmp_path):
    report_path = tmp_path / "test_report.xlsx"
    report_path.write_text("fake excel")

    # Step 1: Successful run
    summary = {
        "MATCHED": 15,
        "CHANGED": 5,
        "MISSING": 2,
        "NEW": 1,
        "DUPLICATE": 0,
        "TOTAL": 23,
    }
    tk_app._on_success(summary, str(report_path))
    assert tk_app.metric_vars["MATCHED"].get() == "15"
    assert str(tk_app.btn_open_report["state"]) == "normal"
    assert str(tk_app.btn_open_folder["state"]) == "normal"

    # Step 2: Start new run -> resets metrics and disables buttons
    tk_app._reset_metrics()
    assert tk_app.metric_vars["MATCHED"].get() == "-"
    assert tk_app.metric_vars["CHANGED"].get() == "-"
    assert "Processing" in tk_app.total_records_var.get()

    # Step 3: Run fails with validation error -> metrics remain cleared, buttons disabled
    tk_app._on_validation_error("Invalid file structure")
    assert tk_app.metric_vars["MATCHED"].get() == "-"
    assert "halted" in tk_app.total_records_var.get()
    assert str(tk_app.btn_open_report["state"]) == "disabled"
    assert str(tk_app.btn_open_folder["state"]) == "disabled"


def test_gui_update_action_buttons_when_file_does_not_exist(tk_app, tmp_path):
    missing_report = tmp_path / "non_existent.xlsx"

    tk_app._update_action_buttons(str(missing_report))

    assert str(tk_app.btn_open_report["state"]) == "disabled"
    assert str(tk_app.btn_open_folder["state"]) == "normal"


def test_gui_validation_warning_on_missing_files(tk_app, monkeypatch):
    warnings = []
    monkeypatch.setattr(
        "tkinter.messagebox.showwarning",
        lambda title, msg: warnings.append((title, msg)),
    )

    # Both empty -> warning for File A
    tk_app._start_reconciliation()
    assert len(warnings) == 1
    assert "File A" in warnings[0][1]

    # File A filled, File B empty -> warning for File B
    tk_app.file_a_var.set("a.xlsx")
    tk_app._start_reconciliation()
    assert len(warnings) == 2
    assert "File B" in warnings[1][1]

    # File B filled, Output empty -> warning for Output
    tk_app.file_b_var.set("b.xlsx")
    tk_app.output_var.set("")
    tk_app._start_reconciliation()
    assert len(warnings) == 3
    assert "output" in warnings[2][1].lower()


def test_gui_extension_validation(tk_app, monkeypatch):
    warnings = []
    monkeypatch.setattr(
        "tkinter.messagebox.showwarning",
        lambda title, msg: warnings.append((title, msg)),
    )

    # .xlsx is valid
    assert tk_app._check_valid_excel_extension("path/to/file.xlsx", "File A") is True
    assert len(warnings) == 0

    # .xls is legacy and rejected with clear message
    assert tk_app._check_valid_excel_extension("path/to/file.xls", "File A") is False
    assert len(warnings) == 1
    assert "legacy Excel (.xls)" in warnings[0][1]
    assert ".xlsx" in warnings[0][1]

    # .csv is unsupported
    assert tk_app._check_valid_excel_extension("path/to/file.csv", "File B") is False
    assert len(warnings) == 2
    assert "unsupported format ('.csv')" in warnings[1][1]


def test_gui_start_reconciliation_aborts_on_unsupported_file_extension(tk_app, monkeypatch):
    warnings = []
    monkeypatch.setattr(
        "tkinter.messagebox.showwarning",
        lambda title, msg: warnings.append((title, msg)),
    )

    tk_app.file_a_var.set("data.xls")
    tk_app.file_b_var.set("data.xlsx")
    tk_app._start_reconciliation()

    assert len(warnings) == 1
    assert "legacy Excel (.xls)" in warnings[0][1]
    assert str(tk_app.btn_run["state"]) == "normal"


def test_gui_on_validation_error_shows_message(tk_app, monkeypatch):
    errors = []
    monkeypatch.setattr(
        "tkinter.messagebox.showerror",
        lambda title, msg: errors.append((title, msg)),
    )

    tk_app._on_validation_error("Customer ID contains empty values")

    assert len(errors) == 1
    assert errors[0][0] == "Validation Error"
    assert "Customer ID contains empty values" in errors[0][1]
    assert "validation error" in tk_app.status_var.get()
    assert str(tk_app.btn_open_report["state"]) == "disabled"
    assert str(tk_app.btn_open_folder["state"]) == "disabled"


def test_gui_on_unexpected_error_shows_message(tk_app, monkeypatch):
    errors = []
    monkeypatch.setattr(
        "tkinter.messagebox.showerror",
        lambda title, msg: errors.append((title, msg)),
    )

    tk_app._on_unexpected_error("Permission denied")

    assert len(errors) == 1
    assert errors[0][0] == "Error"
    assert "Permission denied" in errors[0][1]
    assert "unexpected error" in tk_app.status_var.get()
    assert str(tk_app.btn_open_report["state"]) == "disabled"
    assert str(tk_app.btn_open_folder["state"]) == "disabled"
