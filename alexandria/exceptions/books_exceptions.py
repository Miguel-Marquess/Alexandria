class BookNotFound(Exception):
    def __init__(
        self,
        book_id: int,
    ) -> None:
        self.book_id = book_id


class BookInCurrentLoan(Exception):
    def __init__(self, book_id: int) -> None:
        self.book_id = book_id


class BookNotAvailable(Exception):
    def __init__(self, book_id: int) -> None:
        self.book_id = book_id
