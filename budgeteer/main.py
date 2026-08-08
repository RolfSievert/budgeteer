#! /usr/bin/env python

import argparse
from pathlib import Path

from budgeteer.database import Database
from budgeteer.datetime_utils import localnow
from budgeteer.entities.user_config import UserConfig
from budgeteer.prompts.delete_expense import delete_expenses
from budgeteer.prompts.edit_expenses import edit_expenses
from budgeteer.prompts.enter_expenses import enter_expenses
from budgeteer.prompts.main_menu_options import MainMenuOptions
from budgeteer.prompts.main_meny import main_menu
from budgeteer.prompts.month_menu import month_menu
from budgeteer.prompts.month_menu_options import MonthMenuOptions
from budgeteer.prompts.month_selection import month_selection
from budgeteer.user_config import data_dir, get_user_config


class Args(argparse.Namespace):
    monthly_reminder: str
    database_path: Path
    backup_dir: Path


def parse_program_args(user_config: UserConfig) -> Args:
    parser = argparse.ArgumentParser(
        prog="budgeteer",
        description="A tool for downloading and testing programming problems",
    )

    parser.add_argument(
        "--monthly-reminder",
        default="1 month;1st",
        help="prompt the user to enter expenses if due",
    )
    parser.add_argument(
        "--database-path",
        default=user_config.db_path or data_dir() / "database.sqlite",
        type=Path,
        help="override database path",
    )
    parser.add_argument(
        "--backup-dir",
        default=user_config.backup_dir,
        type=Path,
        help="Export a backup csv of the database in target directory upon exit",
    )

    parsed_args = parser.parse_args(namespace=Args())
    return parsed_args


def run_app(database: Database) -> None:
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
                if month_action == MonthMenuOptions.delete_expenses:
                    delete_expenses(database, year=month.year, month=month.month)

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
                if month_action == MonthMenuOptions.delete_expenses:
                    delete_expenses(database, year=month.year, month=month.month)

                month_action = month_menu(database, year=month.year, month=month.month)


def export_all_data(export_dir: Path, database: Database):
    # create the export path if it does not exist already
    if export_dir:
        export_dir.mkdir(parents=True, exist_ok=True)

    expenses_path = (
        export_dir / f"expenses-{localnow().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
    )
    database.export_expenses_to_csv(expenses_path)

    metadata_path = (
        export_dir / f"metadata-{localnow().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
    )
    database.export_metadata_to_csv(metadata_path)


def main():
    user_config = get_user_config()

    args = parse_program_args(user_config)

    if args.monthly_reminder:
        print("TODO")

    db_path: Path = args.database_path
    # create the db path if it does not exist already
    db_path.parent.mkdir(parents=True, exist_ok=True)

    database = Database(db_path)
    run_app(database)

    export_dir: Path | None = args.backup_dir

    if export_dir:
        export_all_data(export_dir, database)


if __name__ == "__main__":
    main()
