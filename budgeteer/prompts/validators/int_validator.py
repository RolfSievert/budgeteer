from prompt_toolkit.validation import ValidationError, Validator


class IntValidator(Validator):
    def validate(self, document):
        text = document.text

        try:
            int(text)
        except ValueError:
            raise ValidationError(message="Invalid number.")
