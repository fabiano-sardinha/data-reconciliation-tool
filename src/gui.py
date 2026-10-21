import os
import subprocess
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from reconcile import run_reconciliation
from validation import DataValidationError, InputFileError


DEFAULT_OUTPUT_FILE = "output/reconciliation_report.xlsx"


class ReconciliationApp:
    """Professional Tkinter/ttk desktop GUI for Data Reconciliation Tool."""

    def __init__(self, root):
        self.root = root
        self.root.title("Data Reconciliation Tool")
        self.root.geometry("720x660")
        self.root.minsize(640, 580)

        self.file_a_var = tk.StringVar()
        self.file_b_var = tk.StringVar()
        self.output_var = tk.StringVar(value=DEFAULT_OUTPUT_FILE)
        self.status_var = tk.StringVar(value="Select File A and File B to begin.")
        self.total_records_var = tk.StringVar(value="No reconciliation run yet.")

        self.metric_vars = {
            "MATCHED": tk.StringVar(value="-"),
            "CHANGED": tk.StringVar(value="-"),
            "MISSING": tk.StringVar(value="-"),
            "NEW": tk.StringVar(value="-"),
            "DUPLICATE": tk.StringVar(value="-"),
        }

        self._configure_styles()
        self._build_ui()

    def _configure_styles(self):
        self.style = ttk.Style(self.root)
        available_themes = self.style.theme_names()
        if "vista" in available_themes:
            self.style.theme_use("vista")
        elif "clam" in available_themes:
            self.style.theme_use("clam")

        default_font = ("Segoe UI", 9)
        title_font = ("Segoe UI", 14, "bold")
        header_font = ("Segoe UI", 10, "bold")
        metric_num_font = ("Segoe UI", 16, "bold")
        metric_lbl_font = ("Segoe UI", 8, "bold")

        self.style.configure(".", font=default_font)
        self.style.configure("Title.TLabel", font=title_font, foreground="#1e293b")
        self.style.configure("Subtitle.TLabel", font=default_font, foreground="#64748b")
        self.style.configure("Section.TLabelframe.Label", font=header_font, foreground="#334155")
        self.style.configure("Status.TLabel", font=default_font, foreground="#334155")
        self.style.configure("Run.TButton", font=("Segoe UI", 10, "bold"))

        self.metric_colors = {
            "MATCHED": {"bg": "#E8F5E9", "fg": "#1B5E20"},
            "CHANGED": {"bg": "#FFF8E1", "fg": "#B78103"},
            "MISSING": {"bg": "#FFEBEE", "fg": "#B71C1C"},
            "NEW": {"bg": "#E3F2FD", "fg": "#0D47A1"},
            "DUPLICATE": {"bg": "#FBE9E7", "fg": "#BF360C"},
        }

    def _build_ui(self):
        main_container = ttk.Frame(self.root, padding=16)
        main_container.pack(fill="both", expand=True)

        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill="x", pady=(0, 12))
        ttk.Label(
            header_frame,
            text="Data Reconciliation Tool",
            style="Title.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            header_frame,
            text="Compare two Excel workbooks by Customer ID and generate an audit report.",
            style="Subtitle.TLabel",
        ).pack(anchor="w")

        # Inputs section
        inputs_frame = ttk.LabelFrame(main_container, text="Input Workbooks", style="Section.TLabelframe", padding=12)
        inputs_frame.pack(fill="x", pady=(0, 10))

        # File A
        ttk.Label(inputs_frame, text="File A (Reference):").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.entry_a = ttk.Entry(inputs_frame, textvariable=self.file_a_var)
        self.entry_a.grid(row=0, column=1, sticky="ew", padx=6, pady=4)
        self.btn_browse_a = ttk.Button(inputs_frame, text="Browse...", command=self._browse_file_a)
        self.btn_browse_a.grid(row=0, column=2, padx=4, pady=4)

        # File B
        ttk.Label(inputs_frame, text="File B (Comparison):").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.entry_b = ttk.Entry(inputs_frame, textvariable=self.file_b_var)
        self.entry_b.grid(row=1, column=1, sticky="ew", padx=6, pady=4)
        self.btn_browse_b = ttk.Button(inputs_frame, text="Browse...", command=self._browse_file_b)
        self.btn_browse_b.grid(row=1, column=2, padx=4, pady=4)

        inputs_frame.columnconfigure(1, weight=1)

        # Output section
        output_frame = ttk.LabelFrame(main_container, text="Output Destination", style="Section.TLabelframe", padding=12)
        output_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(output_frame, text="Report File:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.entry_out = ttk.Entry(output_frame, textvariable=self.output_var)
        self.entry_out.grid(row=0, column=1, sticky="ew", padx=6, pady=4)
        self.btn_browse_out = ttk.Button(output_frame, text="Change...", command=self._browse_output_file)
        self.btn_browse_out.grid(row=0, column=2, padx=4, pady=4)

        output_frame.columnconfigure(1, weight=1)

        # Action and Progress section
        action_frame = ttk.Frame(main_container)
        action_frame.pack(fill="x", pady=(4, 10))

        self.btn_run = ttk.Button(
            action_frame,
            text="Run Reconciliation",
            style="Run.TButton",
            command=self._start_reconciliation,
        )
        self.btn_run.pack(side="left", padx=(0, 10))

        self.progress_bar = ttk.Progressbar(action_frame, mode="indeterminate", length=180)
        self.progress_bar.pack(side="left", padx=(0, 10), fill="x", expand=True)

        # Status Label
        self.lbl_status = ttk.Label(main_container, textvariable=self.status_var, style="Status.TLabel")
        self.lbl_status.pack(anchor="w", pady=(0, 8))

        # Metrics Card Frame
        metrics_frame = ttk.LabelFrame(
            main_container,
            text="Reconciliation Summary",
            style="Section.TLabelframe",
            padding=12,
        )
        metrics_frame.pack(fill="x", pady=(0, 10))

        cards_container = ttk.Frame(metrics_frame)
        cards_container.pack(fill="x", pady=(0, 6))

        statuses = ["MATCHED", "CHANGED", "MISSING", "NEW", "DUPLICATE"]
        for idx, status in enumerate(statuses):
            card = tk.Frame(
                cards_container,
                bg=self.metric_colors[status]["bg"],
                relief="groove",
                bd=1,
                padx=8,
                pady=6,
            )
            card.grid(row=0, column=idx, sticky="nsew", padx=4)
            cards_container.columnconfigure(idx, weight=1)

            lbl_val = tk.Label(
                card,
                textvariable=self.metric_vars[status],
                bg=self.metric_colors[status]["bg"],
                fg=self.metric_colors[status]["fg"],
                font=("Segoe UI", 16, "bold"),
            )
            lbl_val.pack()

            lbl_name = tk.Label(
                card,
                text=status,
                bg=self.metric_colors[status]["bg"],
                fg=self.metric_colors[status]["fg"],
                font=("Segoe UI", 8, "bold"),
            )
            lbl_name.pack()

        ttk.Label(metrics_frame, textvariable=self.total_records_var, style="Subtitle.TLabel").pack(anchor="w", padx=4)

        # Quick Actions (Open Report / Open Folder)
        bottom_frame = ttk.Frame(main_container)
        bottom_frame.pack(fill="x", pady=(6, 0))

        self.btn_open_report = ttk.Button(
            bottom_frame,
            text="Open Report",
            state="disabled",
            command=self._open_report,
        )
        self.btn_open_report.pack(side="left", padx=(0, 8))

        self.btn_open_folder = ttk.Button(
            bottom_frame,
            text="Open Folder",
            state="disabled",
            command=self._open_folder,
        )
        self.btn_open_folder.pack(side="left")

    def _check_valid_excel_extension(self, file_path: str, label: str) -> bool:
        path = Path(file_path)
        if path.suffix.lower() != ".xlsx":
            if path.suffix.lower() == ".xls":
                msg = (
                    f"{label} ('{path.name}') is in legacy Excel (.xls) format.\n\n"
                    "Only modern Excel (.xlsx) workbooks are supported. "
                    "Please save or export the workbook as .xlsx and try again."
                )
            else:
                msg = (
                    f"{label} ('{path.name}') has an unsupported format ('{path.suffix}').\n\n"
                    "Only modern Excel (.xlsx) workbooks are supported. "
                    "Please select a file with the .xlsx extension."
                )
            messagebox.showwarning("Unsupported Format", msg)
            return False
        return True

    def _browse_file_a(self):
        chosen = filedialog.askopenfilename(
            title="Select File A (Reference)",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        )
        if chosen:
            if not self._check_valid_excel_extension(chosen, "File A"):
                return
            self.file_a_var.set(chosen)

    def _browse_file_b(self):
        chosen = filedialog.askopenfilename(
            title="Select File B (Comparison)",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        )
        if chosen:
            if not self._check_valid_excel_extension(chosen, "File B"):
                return
            self.file_b_var.set(chosen)

    def _browse_output_file(self):
        chosen = filedialog.asksaveasfilename(
            title="Select Output Report Destination",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=Path(self.output_var.get()).name,
        )
        if chosen:
            self.output_var.set(chosen)

    def _reset_metrics(self):
        for var in self.metric_vars.values():
            var.set("-")
        self.total_records_var.set("Processing reconciliation...")

    def _set_inputs_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.btn_run.config(state=state)
        self.btn_browse_a.config(state=state)
        self.btn_browse_b.config(state=state)
        self.btn_browse_out.config(state=state)
        self.entry_a.config(state=state)
        self.entry_b.config(state=state)
        self.entry_out.config(state=state)

    def _start_reconciliation(self):
        file_a = self.file_a_var.get().strip()
        file_b = self.file_b_var.get().strip()
        output_file = self.output_var.get().strip()

        if not file_a:
            messagebox.showwarning("Missing Input", "Please select File A before running reconciliation.")
            return

        if not self._check_valid_excel_extension(file_a, "File A"):
            return

        if not file_b:
            messagebox.showwarning("Missing Input", "Please select File B before running reconciliation.")
            return

        if not self._check_valid_excel_extension(file_b, "File B"):
            return

        if not output_file:
            messagebox.showwarning("Missing Output", "Please specify an output report path.")
            return

        # Reset counters and disable action buttons for the current execution
        self._reset_metrics()
        self._set_inputs_enabled(False)
        self.btn_open_report.config(state="disabled")
        self.btn_open_folder.config(state="disabled")
        self.progress_bar.start(10)
        self.status_var.set("Reconciling workbooks, please wait...")

        # Worker thread keeps GUI fully responsive
        worker = threading.Thread(
            target=self._worker_reconcile,
            args=(file_a, file_b, output_file),
            daemon=True,
        )
        worker.start()

    def _worker_reconcile(self, file_a, file_b, output_file):
        try:
            summary = run_reconciliation(file_a, file_b, output_file)
            self.root.after(0, self._on_success, summary, output_file)
        except (InputFileError, DataValidationError) as error:
            self.root.after(0, self._on_validation_error, str(error))
        except Exception as error:
            self.root.after(0, self._on_unexpected_error, str(error))

    def _on_success(self, summary, output_file):
        self.progress_bar.stop()
        self._set_inputs_enabled(True)

        if isinstance(summary, dict):
            for status, var in self.metric_vars.items():
                var.set(str(summary.get(status, 0)))
            total = summary.get("TOTAL", 0)
            self.total_records_var.set(f"Total: {total} records reconciled.")

        self.status_var.set(f"Reconciliation completed successfully: {output_file}")
        self._update_action_buttons(output_file)

    def _on_validation_error(self, message):
        self.progress_bar.stop()
        self._set_inputs_enabled(True)
        self.btn_open_report.config(state="disabled")
        self.btn_open_folder.config(state="disabled")
        self.total_records_var.set("Reconciliation halted due to validation error.")
        self.status_var.set("Reconciliation halted: validation error.")
        messagebox.showerror("Validation Error", message)

    def _on_unexpected_error(self, message):
        self.progress_bar.stop()
        self._set_inputs_enabled(True)
        self.btn_open_report.config(state="disabled")
        self.btn_open_folder.config(state="disabled")
        self.total_records_var.set("Reconciliation failed due to an error.")
        self.status_var.set("Reconciliation failed: unexpected error.")
        messagebox.showerror("Error", f"An unexpected error occurred:\n{message}")

    def _update_action_buttons(self, output_file):
        out_path = Path(output_file)
        if out_path.is_file():
            self.btn_open_report.config(state="normal")
        else:
            self.btn_open_report.config(state="disabled")

        if out_path.parent.is_dir():
            self.btn_open_folder.config(state="normal")
        else:
            self.btn_open_folder.config(state="disabled")

    def _open_report(self):
        out_path = Path(self.output_var.get().strip())
        if not out_path.is_file():
            messagebox.showwarning("File Not Found", f"Report file not found:\n{out_path}")
            return

        try:
            if sys.platform == "win32":
                os.startfile(str(out_path.resolve()))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(out_path.resolve())], check=False)
            else:
                subprocess.run(["xdg-open", str(out_path.resolve())], check=False)
        except Exception as error:
            messagebox.showerror("Open Report Error", f"Could not open report file:\n{error}")

    def _open_folder(self):
        folder_path = Path(self.output_var.get().strip()).parent
        if not folder_path.is_dir():
            messagebox.showwarning("Folder Not Found", f"Output folder not found:\n{folder_path}")
            return

        try:
            if sys.platform == "win32":
                os.startfile(str(folder_path.resolve()))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(folder_path.resolve())], check=False)
            else:
                subprocess.run(["xdg-open", str(folder_path.resolve())], check=False)
        except Exception as error:
            messagebox.showerror("Open Folder Error", f"Could not open output folder:\n{error}")
