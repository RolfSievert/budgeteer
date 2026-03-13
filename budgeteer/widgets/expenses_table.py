from typing import NamedTuple

from prompt_toolkit import widgets
from prompt_toolkit.layout import Container, HSplit, VSplit

from budgeteer.entities.category import Category
from budgeteer.entities.expense import Expense
from budgeteer.str_utils import date_to_str


class ExpenseColumnWidths(NamedTuple):
    indices: int
    category: int
    price: int
    name: int
    date: int = 10


def expense_row(
    expense: Expense,
    category: Category | None,
    column_widths: ExpenseColumnWidths,
    index: int | None = None,
) -> VSplit:
    def str_or_empty(text: str | None) -> str:
        return f"{text}" if text else ""

    separator = widgets.Label(" | ", dont_extend_height=True, dont_extend_width=True)
    row = [
        widgets.Label(
            date_to_str(expense.date()), width=column_widths.date, wrap_lines=False
        ),
        separator,
        widgets.Label(
            str_or_empty(category.name if category is not None else None),
            width=column_widths.category,
        ),
        separator,
        widgets.Label(str(expense.price), width=column_widths.price, wrap_lines=False),
        separator,
        widgets.Label(expense.name, wrap_lines=True, width=column_widths.name),
        separator,
        widgets.Label(expense.description, wrap_lines=True, dont_extend_width=False),
    ]

    if index is not None:
        row = [
            widgets.Label(str(index), width=column_widths.indices, wrap_lines=False),
            separator,
        ] + row

    return VSplit(row)


__index_header = "INDEX"
__date_header = "DATE"
__category_header = "CATEGORY"
__price_header = "PRICE"
__expense_header = "EXPENSE NAME"
__description_header = "EXPENSE DESCRIPTION"


def table_header(column_widths: ExpenseColumnWidths, indexed: bool) -> VSplit:
    def str_or_empty(text: str | None) -> str:
        return f"{text}" if text else ""

    separator = widgets.Label(" | ", dont_extend_height=True, dont_extend_width=True)
    row = [
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
        widgets.Label(__description_header, wrap_lines=True, dont_extend_width=False),
    ]

    if indexed:
        row = [
            widgets.Label(
                __index_header, width=column_widths.indices, wrap_lines=False
            ),
            separator,
        ] + row

    return VSplit(row)


def expenses_table(
    expenses: list[Expense], categories: dict[int, Category], indexed: bool = False
) -> HSplit:
    column_widths = ExpenseColumnWidths(
        indices=max(
            max(len(str(i)) for i in range(len(expenses))), len(__index_header)
        ),
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

    rows: list[Container] = []
    for i, e in enumerate(expenses):
        rows.append(
            expense_row(
                e,
                categories[e.category_id] if e.category_id is not None else None,
                column_widths,
                index=i + 1 if indexed else None,
            )
        )

    return HSplit(
        [table_header(column_widths, indexed=indexed), widgets.HorizontalLine()]
        + rows
        + [widgets.Label("", dont_extend_height=False)]
    )
