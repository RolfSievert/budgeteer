#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import argparse
from pathlib import Path
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import choice
from .database import Expenses


def main():
    parser = argparse.ArgumentParser(
        prog="budgeteer",
        description="A tool for downloading and testing programming problems",
    )

    args = parser.parse_args()

    if args.command == "new":
        template = None

    database = Expenses()

    result = choice(
        message="Choose an action:",
        options=[
            ("add expenses", "Tool to add expenses one by one with tab completion"),
            ("import/export", "Import or export from/to csv"),
            ("sushi", "Sushi"),
        ],
    )

    print(f"you chose {result}")


if __name__ == "__main__":
    main()
