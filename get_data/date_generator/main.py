import functions_framework
from datetime import date
from flask import jsonify


@functions_framework.http
def current_date(request):
    current_date = date.today()
    output = {"year": current_date.year, "month": current_date.month}
    return jsonify(output)


