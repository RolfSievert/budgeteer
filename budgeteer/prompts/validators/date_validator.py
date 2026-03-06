from datetime import date

from prompt_toolkit.validation import ValidationError, Validator


class DateValidator(Validator):
    def validate(self, document):
        text = document.text

        try:
            date.strptime(text, "%Y-%m-%d")  # ty:ignore[unresolved-attribute]
        except ValueError:
            raise ValidationError(
                message="Date has to be on the format '1994-01-09' (year-month-day)"
            )
