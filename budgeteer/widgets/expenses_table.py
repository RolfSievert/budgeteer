from typing import NamedTuple

from prompt_toolkit import widgets
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import (
    Container,
    HSplit,
    ScrollablePane,
    WindowAlign,
    to_container,
)

from budgeteer.entities.category import Category
from budgeteer.entities.expense import Expense
from budgeteer.str_utils import date_to_str


class ExpenseColumnWidths(NamedTuple):
    indices: int
    category: int
    price: int
    name: int
    date: int = 10


def __add_spaces(text: str, end_length: int, prefix: bool = False) -> str:
    space_count = max(0, end_length - len(text))
    if prefix:
        return " " * space_count + text
    else:
        return text + " " * space_count


def expense_row(
    expense: Expense,
    category: Category | None,
    column_widths: ExpenseColumnWidths,
    index: int | None = None,
) -> str:
    def str_or_empty(text: str | None) -> str:
        return f"{text}" if text else ""

    separator = " │ "

    row = separator.join(
        [
            __add_spaces(date_to_str(expense.date()), column_widths.date),
            __add_spaces(
                str_or_empty(category.name if category else None),
                column_widths.category,
            ),
            __add_spaces(str(expense.price), column_widths.price, prefix=True),
            __add_spaces(expense.name, column_widths.name),
            str_or_empty(expense.description),
        ]
    )

    if index is not None:
        row = __add_spaces(str(index), column_widths.indices) + separator + row

    return row


__index_header = "INDEX"
__date_header = "DATE"
__category_header = "CATEGORY"
__price_header = "PRICE"
__expense_header = "EXPENSE NAME"
__description_header = "EXPENSE DESCRIPTION"


def table_header(column_widths: ExpenseColumnWidths, indexed: bool) -> str:
    def str_or_empty(text: str | None) -> str:
        return f"{text}" if text else ""

    separator = " │ "

    row = separator.join(
        [
            __add_spaces(__date_header, column_widths.date),
            __add_spaces(
                __category_header,
                column_widths.category,
            ),
            __add_spaces(__price_header, column_widths.price),
            __add_spaces(__expense_header, column_widths.name),
            str_or_empty(__description_header),
        ]
    )

    if indexed:
        row = __add_spaces(__index_header, column_widths.indices) + separator + row

    return row


def expenses_table(
    expenses: list[Expense],
    categories: dict[int, Category],
    kb: KeyBindings,
    indexed: bool = False,
) -> Container:
    column_widths = ExpenseColumnWidths(
        indices=max(
            max(len(str(i)) for i in range(len(expenses) if expenses else 1)),
            len(__index_header),
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

    rows: list[str] = []
    for i, e in enumerate(expenses):
        rows.append(
            expense_row(
                e,
                categories[e.category_id] if e.category_id is not None else None,
                column_widths,
                index=i + 1 if indexed else None,
            )
        )

    scrollable_pane = ScrollablePane(
        to_container(widgets.Label("\n".join(rows))),
    )

    def scroll_up(event: KeyPressEvent):
        scrollable_pane.vertical_scroll = max(scrollable_pane.vertical_scroll - 1, 0)

    def scroll_down(event: KeyPressEvent):
        scrollable_pane.vertical_scroll = min(
            scrollable_pane.vertical_scroll + 1, len(expenses) - 1
        )

    kb.add("c-up")(scroll_up)
    kb.add("c-down")(scroll_down)

    return HSplit(
        [
            widgets.Label(
                "Press [CTRL+Up] and [CTRL+Down] to scroll",
                align=WindowAlign.RIGHT,
                dont_extend_height=True,
            ),
            widgets.Label(
                table_header(column_widths, indexed=indexed), dont_extend_height=True
            ),
            widgets.HorizontalLine(),
            scrollable_pane,
        ]
    )
