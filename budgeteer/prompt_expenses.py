from datetime import date

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import ValidationError, Validator

from budgeteer.database import Database
from budgeteer.models.category import Category
from budgeteer.models.expense import Expense
from budgeteer.str_utils import str_to_date


class NonEmptyValidator(Validator):
    def validate(self, document):
        text = document.text

        if not len(text):
            raise ValidationError(message="Entry cannot be empty")

        if not len(text.strip()):
            raise ValidationError(message="Entry cannot be only whitespace")

        if len(text.lstrip()) != len(text):
            raise ValidationError(message="Entry cannot have leading whitespace")

        if len(text.rstrip()) != len(text):
            raise ValidationError(message="Entry cannot have trailing whitespace")


class DateValidator(Validator):
    def validate(self, document):
        text = document.text

        try:
            date.strptime(text, "%Y-%m-%d")  # ty:ignore[unresolved-attribute]
        except ValueError:
            raise ValidationError(
                message="Date has to be on the format '1994-01-09' (year-month-day)"
            )


def prompt_category(database: Database, default: int | None = None) -> Category:
    categories = database.get_categories()
    completer = WordCompleter([x.name for x in categories])
    default_category = next((x.name for x in categories if x.id == default), "")
    result = prompt(
        message="Enter a category: ",
        completer=completer,
        default=default_category,
        validator=NonEmptyValidator(),
    )

    category = next((x for x in categories if x.name == result), None)

    if category is None:
        category = database.new_category(Category(name=result, description=""))

    return category


def create_expense(database: Database, year: int, month: int, day: int) -> Expense:
    expenses = database.get_expenses()
    completer = WordCompleter([expense.name for expense in expenses])
    result = prompt(
        message="Enter an expense: ", completer=completer, validator=NonEmptyValidator()
    )

    expense = next((x for x in expenses if x.name == result), None)
    date = expense.date if expense is not None else None

    def str_or_empty(num: int | None) -> str:
        return f"{num}" if num else ""

    while date is None:
        date_prompt = prompt(
            "Enter a date: ",
            default=f"{(f'{year}-{month}-{str_or_empty(day)}' if month else f'{year}-') if year else ''}",
            validator=DateValidator(),
        )
        date = str_to_date(date_prompt)

    category = expense.category_id if expense is not None else None

    new_expense = database.new_expense(
        Expense(name=result, date=date, category_id=category)
    )

    return new_expense


def prompt_expense(database: Database, year: int, month: int, day: int) -> Expense:
    expense = create_expense(database, year=year, month=month, day=day)
    category = prompt_category(database, default=expense.category_id)

    if expense.category_id != category.id:
        expense = database.update_expense_category(expense.id, category.id)

    return expense


def prompt_expensess(database: Database) -> None:
    year_prompt = prompt("Enter year: ", default=f"{date.today().year}")
    year = int(year_prompt)

    month_prompt = prompt("Enter month: ", default=f"{date.today().month}")
    month = int(month_prompt)

    day = 0

    while True:
        expense = prompt_expense(database, year=year, month=month, day=day)
        day = expense.date.day
