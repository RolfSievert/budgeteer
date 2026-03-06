from datetime import date, datetime

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import ValidationError, Validator

from budgeteer.database import Database
from budgeteer.models.category import Category
from budgeteer.models.expense import Expense
from budgeteer.prompts.validators.date_validator import DateValidator
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


class PriceValidator(Validator):
    def validate(self, document):
        text = document.text

        try:
            float(text)
        except ValueError:
            raise ValidationError(
                message="Invalid price format. Some valid examples: 11.0, 5, 0.1, -20"
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
        category = database.new_category(
            Category(name=result, description="", created_at=datetime.now())
        )

    return category


def prompt_date(year: int, month: int, day: int) -> date:
    def str_or_empty(num: int | None) -> str:
        return f"{num}" if num else ""

    date = None
    while date is None:
        date_prompt = prompt(
            "Enter a date: ",
            default=f"{(f'{year}-{month}-{str_or_empty(day)}' if month else f'{year}-') if year else ''}",
            validator=DateValidator(),
        )
        date = str_to_date(date_prompt)

    return date


def prompt_price() -> float:
    res = prompt(
        "Enter a price: ",
        validator=PriceValidator(),
    )

    return float(res)


def create_expense(database: Database, year: int, month: int, day: int) -> Expense:
    expenses = database.get_expenses()
    expense_names = list({expense.name for expense in expenses})
    completer = WordCompleter(expense_names)
    result = prompt(
        message="Enter an expense: ", completer=completer, validator=NonEmptyValidator()
    )

    price = prompt_price()
    date = prompt_date(year=year, month=month, day=day)

    # use a matching expense to set the default category
    matches = [x for x in expenses if x.name == result]
    latest_expense = max(
        matches,
        key=lambda e: e.created_at,
        default=None,
    )
    category = latest_expense.category_id if latest_expense else None

    new_expense = database.new_expense(
        Expense(
            name=result,
            price=price,
            year=date.year,
            month=date.month,
            day=date.day,
            category_id=category,
            created_at=datetime.now(),
        )
    )

    return new_expense


def prompt_expense(database: Database, year: int, month: int, day: int) -> Expense:
    expense = create_expense(database, year=year, month=month, day=day)
    category = prompt_category(database, default=expense.category_id)

    if expense.category_id != category.id:
        expense = database.update_expense_category(expense, category.id)

    return expense


def prompt_expenses(database: Database, year: int, month: int) -> None:
    day = 0

    while True:
        expense = prompt_expense(database, year=year, month=month, day=day)
        day = expense.day
