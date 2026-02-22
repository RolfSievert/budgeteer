#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import argparse
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import choice
from database import Expenses
from database import Category
from database import Expense


def main():
    parser = argparse.ArgumentParser(
        prog="budgeteer",
        description="A tool for downloading and testing programming problems",
    )

    parser.add_argument("--reminder")

    args = parser.parse_args()

    if args.reminder:
        print("reminder not set up")

    database = Expenses()

    result = choice(
        message="Choose an action:",
        options=[
            ("add expenses", "Tool to add expenses one by one with tab completion"),
            ("import/export", "Import or export from/to csv"),
            ("sushi", "Sushi"),
        ],
    )

    if result == "add expenses":
        add_expenses(database)


def select_category(database: Expenses, default: int | None = None) -> Category:
    categories = database.get_categories()
    completer = WordCompleter([x.name for x in categories])
    default_category = next((x.name for x in categories if x.id == default), "")
    result = prompt(
        message="Enter a category: ", completer=completer, default=default_category
    )

    category = next((x for x in categories if x.name == result), None)

    if category is None:
        category = database.new_category(result, "")

    return category


def create_expense(database: Expenses) -> Expense:
    expenses = database.get_expenses()
    completer = WordCompleter([expense.name for expense in expenses])
    result = prompt(message="Enter an expense: ", completer=completer)

    expense = next((x for x in expenses if x.name == result), None)
    category = expense.category_id if expense is not None else None

    new_expense = database.new_expense(result, category)

    return new_expense


def add_expenses(database: Expenses) -> None:
    expense = create_expense(database)
    category = select_category(database, default=expense.category_id)

    if expense.category_id != category.id:
        expense = database.update_expense_category(expense.id, category.id)

    print("Done!")
    print(f"Entered {expense}")


if __name__ == "__main__":
    main()
