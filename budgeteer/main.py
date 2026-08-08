#! /usr/bin/env python

import argparse
from pathlib import Path

from budgeteer.app_data import (
    default_database_path,
    default_user_settings_path,
    get_user_settings,
)
from budgeteer.database import Database
from budgeteer.entities.program_settings import ProgramSettings
from budgeteer.entities.user_settings import UserSettings
from budgeteer.prompts.delete_expense import delete_expenses
from budgeteer.prompts.edit_expenses import edit_expenses
from budgeteer.prompts.edit_user_settings import edit_user_settings
from budgeteer.prompts.enter_expenses import enter_expenses
from budgeteer.prompts.main_menu_options import MainMenuOptions
from budgeteer.prompts.main_meny import main_menu
from budgeteer.prompts.month_menu import month_menu
from budgeteer.prompts.month_menu_options import MonthMenuOptions
from budgeteer.prompts.month_selection import month_selection
from budgeteer.utils.datetime_utils import localnow


def parse_program_args() -> ProgramSettings:
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
        "--db-path",
        default=None,
        type=Path,
        help="override database location",
    )
    parser.add_argument(
        "--backup-dir",
        default=None,
        type=Path,
        help="exports database as .csv to target directory upon exit",
    )
    parser.add_argument(
        "--user-settings-path",
        default=None,
        type=Path,
        help="override location of user settings",
    )

    class Args(argparse.Namespace):
        monthly_reminder: str
        db_path: Path | None
        backup_dir: Path | None
        user_settings_path: Path | None

    args = parser.parse_args(namespace=Args())
    user_settings = (
        get_user_settings(args.user_settings_path)
        if (args.user_settings_path and args.user_settings_path.is_file())
        else None
    )

    # prioritization: passed args > user settings > defaults
    db_path = args.db_path or (
        user_settings.db_path if user_settings else default_database_path()
    )
    backup_dir = args.backup_dir or (
        user_settings.backup_dir if user_settings else None
    )
    user_settings_path = args.user_settings_path or default_user_settings_path()

    return ProgramSettings(
        user_settings_path=user_settings_path,
        user_settings=UserSettings(db_path=db_path, backup_dir=backup_dir),
    )


def run_app(database: Database, program_settings: ProgramSettings) -> None:
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
        elif option == MainMenuOptions.edit_user_conf:
            user_settings = edit_user_settings(
                program_settings.user_settings_path, program_settings.user_settings
            )

            if (
                user_settings
                and user_settings.db_path != program_settings.user_settings.db_path
            ):
                database.close()
                db_path: Path = user_settings.db_path
                # create the db path if it does not exist already
                db_path.parent.mkdir(parents=True, exist_ok=True)

                database = Database(db_path)

                program_settings = ProgramSettings(
                    user_settings_path=program_settings.user_settings_path,
                    user_settings=user_settings,
                )

    # run backup at end of program
    if program_settings.user_settings.backup_dir:
        export_all_data(program_settings.user_settings.backup_dir, database)


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
    program_settings = parse_program_args()

    db_path: Path = program_settings.user_settings.db_path
    # create the db path if it does not exist already
    db_path.parent.mkdir(parents=True, exist_ok=True)

    database = Database(db_path)
    run_app(database, program_settings)


if __name__ == "__main__":
    main()
