class AuthorNotFound(Exception):
    def __init__(self, author_id):
        self.author_id = author_id
