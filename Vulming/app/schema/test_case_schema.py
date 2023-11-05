from pydantic import BaseModel


class TestCaseBase(BaseModel):
    title: str
    description: str | None = None


class TestCaseCreate(TestCaseBase):
    pass


class TestCase(TestCaseBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True