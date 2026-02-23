#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import argparse
from prompt_toolkit.shortcuts import choice
from add_expense import add_expenses
from database import Expenses


def main():
    parser = argparse.ArgumentParser(
        prog="budgeteer",
        description="A tool for downloading and testing programming problems",
    )

    parser.add_argument("--reminder")
    parser.add_argument("--database", default='')

    args = parser.parse_args()

    if args.reminder:
        print("reminder not set up")

    database = Expenses()

    add_expenses_option = (
        "add expenses",
        "Tool to add expenses one by one with tab completion",
    )
    import_export_option = ("import/export", "Import or export from/to csv")

    result = choice(
        message="Choose an action:",
        options=[
            add_expenses_option,
            import_export_option,
        ],
    )

    if result == add_expenses_option[0]:
        add_expenses(database)


if __name__ == "__main__":
    main()
