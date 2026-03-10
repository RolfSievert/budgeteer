from prompt_toolkit import widgets
from prompt_toolkit.layout import HSplit, VSplit

from budgeteer.models.category import Category
from budgeteer.models.expense import Expense
from budgeteer.widgets.utils.category_costs import category_costs
from budgeteer.widgets.utils.expenses_by_month import Month, expenses_by_month
from budgeteer.widgets.utils.signed import signed


def category_summaries(
    category_map: dict[int, Category],
    costs: dict[int | None, float],
    previous_costs: dict[int | None, float],
) -> widgets.Box:
    def category_summary(
        category_id: int | None, total: float, previous_total: float | None
    ) -> str:
        nonlocal category_map
        diff = total - previous_total if previous_total is not None else total
        name = (
            category_map[category_id].name
            if category_id is not None
            else "uncategorized"
        )
        return f"{name} {int(total)}({signed(int(diff))})"

    category_strings = [
        category_summary(
            category_id=k,
            total=v,
            previous_total=previous_costs[k] if k in previous_costs else None,
        )
        for k, v in sorted(costs.items(), key=lambda item: item[1], reverse=True)
        if k is not None
    ]
    if None in costs:
        category_strings.append(
            category_summary(
                category_id=None,
                total=costs[None],
                previous_total=previous_costs[None] if None in previous_costs else None,
            )
        )

    category_text = "  ".join(category_strings)

    return widgets.Box(
        padding_left=4,
        padding_bottom=0,
        padding_right=0,
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
    )


def month_summary(
    month: Month,
    expenses: list[Expense],
    previous_month: list[Expense],
    category_map: dict[int, Category],
) -> widgets.Box:
    total = sum(e.price for e in expenses)
    previous_total = sum(e.price for e in previous_month)
    diff = total - previous_total
    return widgets.Box(
        padding_bottom=1,
        padding_left=0,
        padding_right=0,
        padding_top=0,
        body=HSplit(
            [
                widgets.Label(
                    f"{month.format('%Y %B')} > Total {int(total)}({signed(diff)})",
                    style="bold",
                ),
                category_summaries(
                    category_map=category_map,
                    costs=category_costs(expenses),
                    previous_costs=category_costs(previous_month),
                ),
            ]
        ),
    )


def monthly_summaries(
    expenses: list[Expense], category_map: dict[int, Category]
) -> widgets.Box:
    months = expenses_by_month(expenses)

    month_count = len(months)

    if not month_count:
        return widgets.Box(
            padding_top=1,
            body=VSplit(
                [
                    widgets.Label(
                        "No reported expenses. Add some to see a monthly summary here!"
                    )
                ]
            ),
        )

    summaries: list[widgets.Box] = []
    old: Month | None = None
    for m, e in ((k, v) for k, v in sorted(months.items(), key=lambda kvp: kvp[0])):
        if old is None:
            old = m

        summaries.append(
            month_summary(
                month=m,
                expenses=e,
                previous_month=months[old],
                category_map=category_map,
            )
        )
        old = m

    return widgets.Box(
        padding_top=1,
        padding_left=1,
        padding_bottom=0,
        padding_right=0,
        body=HSplit(list(reversed(summaries))),
    )
