from sqlite3 import Connection


class Migration:
    def __init__(self, version: int, description: str, up: str, down: str):
        self.version = version
        self.description = description
        self._up = up
        self._down = down

    def up(self, conn: Connection):
        cursor = conn.cursor()
        cursor.execute(self._up)

        conn.commit()

    def down(self, conn: Connection):
        cursor = conn.cursor()
        cursor.execute(self._down)

        conn.commit()
