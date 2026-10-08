from reconcile import run_reconciliation


file_a = "input/customers_a.xlsx"
file_b = "input/customers_b.xlsx"
output_file = "output/reconciliation_report.xlsx"


run_reconciliation(file_a, file_b, output_file)