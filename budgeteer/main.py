#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from prompt_expenses import prompt_expensess
from database import Database

import argparse
from prompt_toolkit.shortcuts import choice
from pathlib import Path
from platformdirs import PlatformDirs


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
        "--sync-csv-on-exit",
        default=None,
        type=Path,
        help="save data to a csv upon exit",
    )

    args = parser.parse_args()

    if args.reminder:
        print("TODO")

    db_path: Path = args.database_path
    # create the db path if it does not exist already
    db_path.parent.mkdir(parents=True, exist_ok=True)

    database = Database(db_path)

    while program_loop(db=database, sync_csv=args.sync_csv_on_exit):
        pass


def program_loop(db: Database, sync_csv: Path | None) -> bool:
    add_expenses_option = (
        "add expenses",
        "Tool to add expenses one by one with tab completion",
    )
    import_export_option = ("import/export", "Import or export from/to csv")
    quit_option = ("quit", "")

    result = choice(
        message="Choose an action:",
        options=[add_expenses_option, import_export_option, quit_option],
    )

    if result == add_expenses_option[0]:
        prompt_expensess(db)
        pass

    if result == quit_option[0]:
        if sync_csv:
            db.export(sync_csv)
        return False

    # return true to continue running the program
    return True


if __name__ == "__main__":
    main()
