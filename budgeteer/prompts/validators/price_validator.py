from prompt_toolkit.validation import ValidationError, Validator


class PriceValidator(Validator):
    def validate(self, document):
        text = document.text

        try:
            float(text)
        except ValueError:
            raise ValidationError(
                message="Invalid price format. Some valid examples: 11.0, 5, 0.1, -20"
            )
