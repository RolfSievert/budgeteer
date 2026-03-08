#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
import argparse
from datetime import datetime
from pathlib import Path

from platformdirs import PlatformDirs

from budgeteer.database import Database
from budgeteer.prompts.edit_expenses import edit_expenses
from budgeteer.prompts.enter_expenses import enter_expenses
from budgeteer.prompts.main_menu_options import MainMenuOptions
from budgeteer.prompts.main_meny import main_menu
from budgeteer.prompts.month_menu import month_menu
from budgeteer.prompts.month_menu_options import MonthMenuOptions
from budgeteer.prompts.month_selection import month_selection


def data_dir() -> Path:
    dirs = PlatformDirs("budgeteer", "RolfSievert")
    return dirs.user_data_path


def main():
    parser = argparse.ArgumentParser(
        prog="budgeteer",
        description="A tool for downloading and testing programming problems",
    )

    parser.add_argument(
        "--reminder",
        default="1 month;1st",
        help="prompt the user to enter expenses if due",
    )
    parser.add_argument(
        "--database-path",
        default=data_dir() / "database.sqlite",
        type=Path,
        help="override database path",
    )
    parser.add_argument(
        "--backup-dir",
        default=None,
        type=Path,
        help="Export a backup csv of the database in target directory upon exit",
    )

    args = parser.parse_args()

    if args.reminder:
        print("TODO")

    export_dir: Path = args.backup_dir
    if not export_dir.is_dir():
        raise RuntimeError(f"Export dir '{export_dir}' does not exist")

    db_path: Path = args.database_path
    # create the db path if it does not exist already
    db_path.parent.mkdir(parents=True, exist_ok=True)

    database = Database(db_path)

    while True:
        option = main_menu(db=database)

        if option == MainMenuOptions.quit or option is None:
            break
        elif option == MainMenuOptions.add_expenses:
            month = month_selection(database)
            if not month:
                continue

            month_action = MonthMenuOptions.add_expenses
            while month_action not in (None, MonthMenuOptions.exit_menu):
                if month_action == MonthMenuOptions.add_expenses:
                    enter_expenses(database, year=month.year, month=month.month)
                if month_action == MonthMenuOptions.edit_expenses:
                    edit_expenses(database, year=month.year, month=month.month)

                month_action = month_menu(database, year=month.year, month=month.month)
        elif option == MainMenuOptions.edit_month:
            month = month_selection(database)
            if not month:
                continue

            month_action = month_menu(database, year=month.year, month=month.month)
            while month_action not in (None, MonthMenuOptions.exit_menu):
                if month_action == MonthMenuOptions.add_expenses:
                    enter_expenses(database, year=month.year, month=month.month)
                if month_action == MonthMenuOptions.edit_expenses:
                    edit_expenses(database, year=month.year, month=month.month)

                month_action = month_menu(database, year=month.year, month=month.month)

    if export_dir:
        csv_path = (
            export_dir / f"expenses-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
        )
        database.export_expenses_to_csv(csv_path)


if __name__ == "__main__":
    main()
