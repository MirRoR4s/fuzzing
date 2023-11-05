

class User:

    def __init__(self, username: str, password: str, email: str = None, id: int = None, cases=None, disable: bool | None = None, token: str | None = None) -> None:
        self.username = username
        self.password = password
        self.email = email
        self.id = id
        self.cases = cases
        self.disable = disable
        self.token = token