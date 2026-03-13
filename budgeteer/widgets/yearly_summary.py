from datetime import date

from prompt_toolkit import widgets
from prompt_toolkit.layout import Container, HSplit, VSplit

from budgeteer.entities.category import Category
from budgeteer.entities.expense import Expense
from budgeteer.widgets.utils.category_costs import category_costs
from budgeteer.widgets.utils.expenses_by_month import Month, expenses_by_month
from budgeteer.widgets.utils.signed import signed


def sum_price(expenses: list[Expense]) -> float:
    return sum(e.price for e in expenses)


def yearly_summary(
    expenses: list[Expense], category_map: dict[int, Category]
) -> Container:
    today = date.today()
    expenses = [e for e in expenses if e.date() >= date(today.year - 1, today.month, 1)]
    months = expenses_by_month(expenses)

    month_count = len(months)

    if not month_count:
        return VSplit(
            [
                widgets.Label(
                    "No reported expenses last year. Add some to see a summary here!"
                )
            ]
        )

    total = 0
    latest_month: Month = next(iter(months.keys()))
    for m in months:
        s = sum_price(months[m])
        total += s
        if m > latest_month:
            latest_month = m
    average = total / month_count
    total_without_last = total - sum_price(months[latest_month])
    average_without_last = (
        total_without_last / (month_count - 1) if month_count > 1 else average
    )
    diff = average - average_without_last

    costs = category_costs(expenses)
    costs_last_month = category_costs(
        [
            e
            for e in expenses
            if e.year == latest_month.year and e.month == latest_month.month
        ]
    )

    def category_summary(category_id: int | None, total: float) -> str:
        nonlocal category_map
        average = total / month_count
        total_without_last = (
            total - costs_last_month[category_id]
            if category_id in costs_last_month
            else 0
        )
        average_without_last = (
            total_without_last / (month_count - 1) if month_count > 1 else average
        )
        diff = average - average_without_last
        name = (
            category_map[category_id].name
            if category_id is not None
            else "uncategorized"
        )
        return f"{name} {int(average)}({signed(int(diff))})"

    category_strings = [
        category_summary(k, v)
        for k, v in sorted(costs.items(), key=lambda item: item[1], reverse=True)
        if k is not None
    ]
    if None in costs:
        category_strings.append(category_summary(None, costs[None]))

    category_text = "  ".join(category_strings)

    v_separator = widgets.Label(" ", dont_extend_height=True, dont_extend_width=True)
    inner_separator = widgets.Label(
        "  ", dont_extend_height=True, dont_extend_width=True
    )

    return HSplit(
        [
            widgets.Box(
                padding_left=1,
                padding_bottom=0,
                padding_right=1,
                padding_top=1,
                style="reverse",
                body=VSplit(
                    [
                        widgets.Label(
                            "<< LAST YEAR >>",
                            dont_extend_height=True,
                            dont_extend_width=True,
                            style="bold",
                        ),
                        v_separator,
                        widgets.Label(
                            f"Total:{int(total)}",
                            dont_extend_height=True,
                            dont_extend_width=True,
                        ),
                        inner_separator,
                        widgets.Label(
                            f"Average:{int(average)}/month ({signed(int(diff))} last month)",
                            dont_extend_height=True,
                            dont_extend_width=True,
                        ),
                        # empty label to align other text to left
                        widgets.Label(
                            "", dont_extend_height=True, dont_extend_width=False
                        ),
                    ]
                ),
            ),
            widgets.Box(
                padding_left=1,
                padding_bottom=1,
                padding_right=1,
                padding_top=0,
                style="bg:ansigray",
                body=widgets.Box(
                    padding_left=2,
                    padding_right=1,
                    padding_top=0,
                    padding_bottom=0,
                    style="bg:ansiblack fg:ansigray",
                    body=widgets.Label(category_text, dont_extend_height=True),
                ),
            ),
        ]
    )
