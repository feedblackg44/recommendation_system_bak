import argparse

import xlwings as xw


def get_or_create_sheet(book, sheet_name):
    try:
        return book.sheets[sheet_name]
    except KeyError:
        return book.sheets.add(sheet_name)


def set_column_and_row_formatting(sheet):
    sheet.range('A:AB').column_width = 8.6
    sheet.range('1:1').api.WrapText = True
    first_row = sheet.range("1:1")
    first_row.api.HorizontalAlignment = xw.constants.HAlign.xlHAlignLeft
    first_row.api.VerticalAlignment = xw.constants.VAlign.xlVAlignBottom
    first_row.api.Font.Bold = False
    first_row.api.Borders.LineStyle = None


def generate_column_names(headers):
    names = {}
    start_value = ord('A')
    for i, key in enumerate(headers):
        column = i // 26
        remainder = i % 26
        if column == 0:
            value = chr(start_value + remainder)
        else:
            value = chr(start_value + column - 1) + chr(start_value + remainder)
        names[key] = value
    return names


def insert_headers(sheet, headers):
    for key, value in headers.items():
        if sheet[value + '1'].value != key:
            sheet.range(f'{value}:{value}').api.Insert()
            sheet[value + '1'].value = key


def apply_formulas(sheet, formulas, headers):
    for key, formula in formulas.items():
        sheet[f'{headers[key]}2'].value = formula


def autofill_formulas(sheet, formulas, headers):
    last_row = sheet.range("B1").end("down").row
    if last_row > 2:
        for letter in [headers[key] for key in formulas.keys()]:
            range_str = f'{letter}2:{letter}{last_row}'
            sheet.range(f'{letter}2').api.AutoFill(sheet.range(range_str).api, 0)


def main(filename=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--excelname", help="Excel file name")
    args = parser.parse_args()
    filename = filename or args.excelname

    app = xw.App(visible=False)

    book = app.books.open(filename)
    sheet1 = book.sheets['Sheet1']
    sheet3 = book.sheets['Sheet3']

    set_column_and_row_formatting(sheet1)
    sheet1.range("A2").select()
    sheet1.api.Application.ActiveWindow.FreezePanes = True
    xw.apps.active.api.SendKeys("{ESC}")

    sheet3.range('A:A').column_width = 15
    set_column_and_row_formatting(sheet3)

    max_days = round(book.sheets['Sheet4'].range('A2').value)
    can_be_sold_total = f'Can be sold in {max_days} days'

    headers_sheet1 = ['Deal ID', 'Item No', 'Item Name', 'Used Minimum Order Quantity', 'Deal Sum', 'Purchase Price',
                      'Sale Price', 'Profit', 'Average Daily Sales', 'Empty ADS Deal', 'Inventory',
                      'Can be sold in credit terms', can_be_sold_total, 'System Suggested Quantity',
                      'Optimization suggested quantity', 'Overstock',
                      'Days For Sale', 'Deal Days Dispersion', 'Item Budget', 'Budget', 'Total Item Sales',
                      'Total Item Profit', '30 Days Profit', '30 Days Sales',
                      'Weighted Average 30 Day Profit Margin', 'Effectiveness', 'Average Effectiveness', 'AddToTotal',
                      'Included', 'Days For Sale Average', 'Days For Sale sub', 'Overstock check',
                      'Overstock check sum', 'Daily Sales', 'Empty ADS Check Profit']

    headers_sheet3 = ['Deal ID', 'ABC', 'Daily Sales', 'MaxOQ', 'OSQ', 'SSQ']

    names1 = generate_column_names(headers_sheet1)

    names3 = generate_column_names(headers_sheet3)

    insert_headers(sheet1, names1)
    insert_headers(sheet3, names3)

    formulas_sheet1 = {
        'Used Minimum Order Quantity': f'=MAXIFS(Sheet2!D:D, Sheet2!B:B, {names1["Item No"]}2, Sheet2!D:D, '
                                       f'"<="&{names1["Deal Sum"]}2)',
        'Deal Sum': f'=SUMIF({names1["Deal ID"]}:{names1["Deal ID"]}, {names1["Deal ID"]}2, '
                    f'{names1["Optimization suggested quantity"]}:{names1["Optimization suggested quantity"]})',
        'Empty ADS Deal': f'=IF(AND(SUMIFS({names1["Average Daily Sales"]}:{names1["Average Daily Sales"]},'
                          f'{names1["Deal ID"]}:{names1["Deal ID"]},{names1["Deal ID"]}2)<=0,'
                          f'COUNTIFS({names1["Deal ID"]}:{names1["Deal ID"]},{names1["Deal ID"]}2,'
                          f'{names1["Empty ADS Check Profit"]}:{names1["Empty ADS Check Profit"]},"<0")),"empty","OK")',
        'Purchase Price': f'=MINIFS(Sheet2!E:E, Sheet2!B:B, {names1["Item No"]}2, Sheet2!D:D, '
                          f'"<="&{names1["Deal Sum"]}2)',
        'Profit': f'={names1["Sale Price"]}2 - {names1["Purchase Price"]}2',
        can_be_sold_total: f'=MAX(0, {names1["Average Daily Sales"]}2 * Sheet4!$A$2 - {names1["Inventory"]}2)',
        'Overstock': f'=IF({names1["Overstock check sum"]}2,"check","OK")',
        'Days For Sale': f'=IF({names1["Average Daily Sales"]}2 > 0, ({names1["Inventory"]}2 + '
                         f'{names1["Optimization suggested quantity"]}2) / {names1["Average Daily Sales"]}2, 0)',
        'Deal Days Dispersion': f'=IF(COUNTIFS({names1["Deal ID"]}:{names1["Deal ID"]}, {names1["Deal ID"]}2, '
                                f'{names1["Included"]}:{names1["Included"]}, TRUE) > 0, '
                                f'AVERAGEIFS({names1["Days For Sale sub"]}:{names1["Days For Sale sub"]}, '
                                f'{names1["Deal ID"]}:{names1["Deal ID"]}, {names1["Deal ID"]}2, '
                                f'{names1["Included"]}:{names1["Included"]}, TRUE) / COUNTIFS({names1["Deal ID"]}:'
                                f'{names1["Deal ID"]}, {names1["Deal ID"]}2, {names1["Included"]}:'
                                f'{names1["Included"]}, TRUE), 0)',
        'Item Budget': f'={names1["Purchase Price"]}2 * {names1["Optimization suggested quantity"]}2',
        'Budget': f'=SUM({names1["Item Budget"]}:{names1["Item Budget"]})',
        'Total Item Sales': f'={names1["Sale Price"]}2 * {names1["Optimization suggested quantity"]}2',
        'Total Item Profit': f'={names1["Optimization suggested quantity"]}2 * {names1["Profit"]}2',
        '30 Days Profit': f'={names1["Profit"]}2 * MIN({names1["Optimization suggested quantity"]}2, '
                          f'MAX(30 * {names1["Average Daily Sales"]}2 - {names1["Inventory"]}2, 0))',
        '30 Days Sales': f'={names1["Sale Price"]}2 * MIN({names1["Optimization suggested quantity"]}2, '
                         f'MAX(30 * {names1["Average Daily Sales"]}2 - {names1["Inventory"]}2, 0))',
        'Weighted Average 30 Day Profit Margin': f'={names1["30 Days Profit"]}2 / SUM({names1["30 Days Sales"]}:'
                                                 f'{names1["30 Days Sales"]})',
        'Effectiveness': f'={names1["30 Days Profit"]}2 - {names1["Deal Days Dispersion"]}2',
        'Average Effectiveness': f'=SUM({names1["Effectiveness"]}:{names1["Effectiveness"]})',
        'Included': f'=IF({names1["Average Daily Sales"]}2 > 0, ({names1["Inventory"]}2 + '
                    f'{names1["System Suggested Quantity"]}2) / {names1["Average Daily Sales"]}2 <= Sheet4!$A$2 + '
                    f'{names1["AddToTotal"]}2 / {names1["Average Daily Sales"]}2, FALSE)',
        'Days For Sale Average': f'=IF({names1["Included"]}2, AVERAGEIFS({names1["Days For Sale"]}:'
                                 f'{names1["Days For Sale"]}, {names1["Deal ID"]}:{names1["Deal ID"]}, '
                                 f'{names1["Deal ID"]}2, {names1["Included"]}:{names1["Included"]}, TRUE), 0)',
        'Days For Sale sub': f'=IF({names1["Average Daily Sales"]}2 > 0, ({names1["Days For Sale"]}2 - '
                             f'{names1["Days For Sale Average"]}2)^2, 0)',
        'Overstock check': f'=IF(AND({names1["Days For Sale"]}2>Sheet4!$A$2, '
                           f'{names1["Optimization suggested quantity"]}2>0), '
                           f'IF(AND({names1["System Suggested Quantity"]}2=1, '
                           f'{names1["Optimization suggested quantity"]}2=1), 0, 1), 0)',
        'Overstock check sum': f'=SUMIF({names1["Deal ID"]}:{names1["Deal ID"]}, {names1["Deal ID"]}2, '
                               f'{names1["Overstock check"]}:{names1["Overstock check"]})',
        'Daily Sales': f'={names1["Sale Price"]}2 * {names1["Average Daily Sales"]}2',
        'Empty ADS Check Profit': f'={names1["Profit"]}2 * {names1["Optimization suggested quantity"]}2'
    }

    formulas_sheet3 = {
        'Daily Sales': f'=SUMIF(Sheet1!{names1["Deal ID"]}:{names1["Deal ID"]}, {names3["Deal ID"]}2, '
                       f'Sheet1!{names1["Daily Sales"]}:{names1["Daily Sales"]})',
        'MaxOQ': f'=MAXIFS(Sheet2!D:D, Sheet2!A:A, {names3["Deal ID"]}2)',
        'OSQ': f'=SUMIF(Sheet1!{names1["Deal ID"]}:{names1["Deal ID"]}, {names3["Deal ID"]}2, '
               f'Sheet1!{names1["Optimization suggested quantity"]}:{names1["Optimization suggested quantity"]})',
        'SSQ': f'=SUMIF(Sheet1!{names1["Deal ID"]}:{names1["Deal ID"]}, {names3["Deal ID"]}2, '
               f'Sheet1!{names1["System Suggested Quantity"]}:{names1["System Suggested Quantity"]})'
    }

    apply_formulas(sheet1, formulas_sheet1, names1)
    apply_formulas(sheet3, formulas_sheet3, names3)

    autofill_formulas(sheet1, formulas_sheet1, names1)
    autofill_formulas(sheet3, formulas_sheet3, names3)

    sheet1.range(f'{names1["Effectiveness"]}:{names1["Empty ADS Check Profit"]}').api.EntireColumn.Hidden = True
    sheet1.range(f'{names1["Optimization suggested quantity"]}:{names1["Optimization suggested quantity"]}').color = (
        146, 208, 80
    )

    book.save()
    book.close()
    if len(app.books) == 0:
        app.quit()

    print('Formulas filled successfully')


if __name__ == '__main__':
    file_name = '../../output/13.05.2024/test - Copy.xlsx'
    main(file_name)
