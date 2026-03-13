from budgeteer.entities.expense import Expense
from budgeteer.models.month import Month


def expenses_by_month(expenses: list[Expense]) -> dict[Month, list[Expense]]:
    res: dict[Month, list[Expense]] = {}

    for e in expenses:
        month = Month(year=e.year, month=e.month)
        if month not in res:
            res[month] = []
        res[month].append(e)

    return res
