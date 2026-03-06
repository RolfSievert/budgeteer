from datetime import date

from prompt_toolkit.validation import ValidationError, Validator


class MonthValidator(Validator):
    def validate(self, document):
        text = document.text

        try:
            date.strptime(text, "%Y-%m")  # ty:ignore[unresolved-attribute]
        except ValueError:
            raise ValidationError(
                message="Month has to be on the format '1994-01' (year-month)"
            )
