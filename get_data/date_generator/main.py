import functions_framework
from datetime import date
from flask import jsonify


def compute_last_year_month(current_date):
    if current_date.month == 1:
        year = current_date.year - 1
        month = 12
    else:
        year = current_date.year
        month = current_date.month - 1

    return year, month

@functions_framework.http
def current_date(request):
    current_date = date.today()
    last_month_year, last_month = compute_last_year_month(current_date)
    output = {"year": last_month_year, "month": last_month}
    return jsonify(output)


