from typing import NamedTuple


# Metadata related to the vault (not user settings)
class Metadata(NamedTuple):
    start_page_note: str | None

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(start_page_note={self.start_page_note})"

    def to_sql(self) -> dict:
        return {
            "start_page_note": self.start_page_note,
        }

    def sql_values(self) -> str:
        """
        Returns placeholder names for the object, like ":id, :created_at, ..."
        """
        prepended = [":" + tag for tag in self.to_sql()]
        return ", ".join(prepended)

    def table_name() -> str:
        return "metadata"


def metadata_from_sql(sql: dict) -> Metadata:
    return Metadata(
        start_page_note=sql["start_page_note"],
    )
