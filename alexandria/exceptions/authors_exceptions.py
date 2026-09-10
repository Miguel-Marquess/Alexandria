class AuthorNotFound(Exception):
    def __init__(self, author_id: int) -> None:
        self.author_id = author_id


class AuthorNone(Exception): ...


class AuthorHasRegisteredBooks(Exception):
    def __init__(self, author_id: int) -> None:
        self.author_id = author_id
