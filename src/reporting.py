from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import FormulaRule


def create_excel_report(result_df, output_file):

    # Substituir valores vazios por células vazias
    result_df = result_df.fillna("")

    # Salvar relatório em Excel
    result_df.to_excel(output_file, index=False)

    # Abrir o arquivo gerado para aplicar formatação
    workbook = load_workbook(output_file)
    worksheet = workbook.active

    # Formatação do cabeçalho
    for cell in worksheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    # Congelar a primeira linha
    worksheet.freeze_panes = "A2"

    # Ativar filtros
    worksheet.auto_filter.ref = worksheet.dimensions

    # Ajustar largura das colunas
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

    # Alinhar os dados
    for row in worksheet.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="center")

    # Formatação condicional para o Status
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

    # Salvar novamente
    workbook.save(output_file)

    print(f"\nRelatório criado com sucesso: {output_file}")