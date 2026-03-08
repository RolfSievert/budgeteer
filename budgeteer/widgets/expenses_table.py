from typing import NamedTuple

from prompt_toolkit import widgets
from prompt_toolkit.layout import HSplit, VSplit

from budgeteer.models.category import Category
from budgeteer.models.expense import Expense
from budgeteer.str_utils import date_to_str


class ExpenseColumnWidths(NamedTuple):
    category: int
    price: int
    name: int
    date: int = 10


def expense_row(
    expense: Expense, category: Category | None, column_widths: ExpenseColumnWidths
) -> VSplit:
    def str_or_empty(text: str | None) -> str:
        return f"{text}" if text else ""

    separator = widgets.Label(" | ", dont_extend_height=True, dont_extend_width=True)
    return VSplit(
        [
            widgets.Label(
                date_to_str(expense.date()), width=column_widths.date, wrap_lines=False
            ),
            separator,
            widgets.Label(
                str_or_empty(category.name if category is not None else None),
                width=column_widths.category,
            ),
            separator,
            widgets.Label(
                str(expense.price), width=column_widths.price, wrap_lines=False
            ),
            separator,
            widgets.Label(expense.name, wrap_lines=True, width=column_widths.name),
            separator,
            widgets.Label(
                expense.description, wrap_lines=True, dont_extend_width=False
            ),
        ]
    )


__date_header = "DATE"
__category_header = "CATEGORY"
__price_header = "PRICE"
__expense_header = "EXPENSE NAME"
__description_header = "EXPENSE DESCRIPTION"


def table_header(column_widths: ExpenseColumnWidths) -> VSplit:
    def str_or_empty(text: str | None) -> str:
        return f"{text}" if text else ""

    separator = widgets.Label(" | ", dont_extend_height=True, dont_extend_width=True)
    return VSplit(
        [
            widgets.Label(__date_header, width=column_widths.date, wrap_lines=False),
            separator,
            widgets.Label(
                __category_header,
                width=column_widths.category,
            ),
            separator,
            widgets.Label(__price_header, width=column_widths.price, wrap_lines=False),
            separator,
            widgets.Label(__expense_header, wrap_lines=True, width=column_widths.name),
            separator,
            widgets.Label(
                __description_header, wrap_lines=True, dont_extend_width=False
            ),
        ]
    )


def expenses_table(expenses: list[Expense], categories: dict[int, Category]) -> HSplit:
    column_widths = ExpenseColumnWidths(
        category=max(
            len(__category_header),
            max(
                (
                    len(categories[e.category_id].name)
                    for e in expenses
                    if e.category_id is not None and e.category_id in categories
                ),
                default=0,
            ),
        ),
        price=max(
            len(__price_header), max((len(str(e.price)) for e in expenses), default=0)
        ),
        name=max(
            len(__expense_header), max((len(e.name) for e in expenses), default=0)
        ),
    )

    return HSplit(
        [table_header(column_widths), widgets.HorizontalLine()]
        + [
            expense_row(
                e,
                categories[e.category_id] if e.category_id is not None else None,
                column_widths,
            )
            for e in expenses
        ]
        + [widgets.Label("", dont_extend_height=False)]
    )
