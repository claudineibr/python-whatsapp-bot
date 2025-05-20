from .._BaseConnection import DatabaseConnection


class WhatsAppRepository(DatabaseConnection):
    def __init__(self) -> None:
        super().__init__("whatsapp")

    def test_connection(self):
        with self.db_session() as session:
            pass
