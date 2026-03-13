from budgeteer.entities.expense import Expense


def category_costs(expenses: list[Expense]) -> dict[int | None, float]:
    costs: dict[int | None, float] = {}
    for e in expenses:
        if e.category_id not in costs:
            costs[e.category_id] = 0
        costs[e.category_id] += e.price

    return costs
