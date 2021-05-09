import time
from datetime import date

from flask import jsonify

from main import app, auth
from main.enums import Topic
from main.models.question import QuestionModel
from main.models.transaction import TransactionModel


def _get_last_x_months(x):
    now = time.localtime()
    return [time.localtime(time.mktime((now.tm_year, now.tm_mon - n, 1, 0, 0, 0, 0, 0, 0)))[:2] for n in range(x)]


DAYS_BY_MONTH = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31,
}

NAME_BY_MONTH = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}


@app.route('/admin/statistics', methods=['GET'])
@auth.requires_token_auth('admin')
def get_statistics(admin):
    questions = QuestionModel.query.all()
    total_math_questions = 0
    total_english_questions = 0

    transactions = TransactionModel.query.all()

    for question in questions:
        if question.topic_id == Topic.MATH:
            total_math_questions += 1
        if question.topic_id == Topic.ENGLISH:
            total_english_questions += 1

    package_items = {}
    for transaction in transactions:
        if package_items.get(transaction.package_name):
            package_items[transaction.package_name] += 1
        else:
            package_items[transaction.package_name] = 1

    months = _get_last_x_months(12)  # A year

    revenue_items = []
    for (year, month) in months:
        total = 0
        start = date(year=year, month=month, day=1)
        end = date(year=year, month=month, day=DAYS_BY_MONTH[month])

        transactions = TransactionModel.query \
            .filter(TransactionModel.created <= end) \
            .filter(TransactionModel.created >= start) \

        for transaction in transactions:
            total += transaction.amount

        revenue_items.append({
            "name": str(NAME_BY_MONTH[month]) + ", " + str(year),
            "value": total,
        })

    return jsonify({
        "asked_questions": [{
            "name": "Math",
            "value": total_math_questions,
        }, {
            "name": "English",
            "value": total_english_questions,
        }],
        "bought_packages": package_items,
        "revenue": revenue_items,
    })
