import pytest
from services.fuzzing_services import FuzzingService
from services.sql_model import Block
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

engine = create_engine('sqlite+pysqlite:///./test.db')
Session = sessionmaker(bind=engine)

@pytest.fixture
def db_session():
        session = Session()
        yield session
        session.rollback()

class TestSetBlock:
    """
    Test strategy:
    1. Valid input with no conflicts.
    2. Duplicate entry for the same (request_id, name).
    3. Invalid request_id (e.g., negative value).
    4. Negative default_value.
    5. No default_value specified.
    """
        
    def test_set_block_valid_input(self, db_session):
        # Partition: Valid input with no conflicts
        your_instance = FuzzingService(db_session)
        your_instance.set_block(request_id=1, name="ValidBlock4", default_value=42)
        block = db_session.query(Block).filter_by(request_id=1, name="ValidBlock4", default_value=42).first()
        assert block is not None
        stmt = delete(Block).filter_by(request_id=1, name="ValidBlock4", default_value=42)
        db_session.execute(stmt)
        db_session.commit()

    def test_set_block_duplicate_entry(self, db_session):
        # Partition: Duplicate entry for the same (request_id, name)
        fuzzing_service = FuzzingService(db_session)
        duplicate_block = Block(request_id=2, name="DuplicateBlock", default_value=42)
        db_session.add(duplicate_block)
        db_session.commit()
        with pytest.raises(ValueError):
            fuzzing_service.set_block(request_id=2, name="DuplicateBlock", default_value=42)

    # def test_set_block_invalid_request_id(self, db_session):
    #     # Partition: Invalid request_id (e.g., negative value)
    #     your_instance = FuzzingService(db_session)
    #     with pytest.raises(ValueError):
    #         your_instance.set_block(request_id=-1, name="InvalidBlock", default_value=42)

    # def test_set_block_negative_default_value(self, db_session):
    #     # Partition: Negative default_value
    #     your_instance = FuzzingService(db_session)
    #     your_instance.set_block(request_id=3, name="NegativeDefault", default_value=-5)
    #     block = db_session.query(Block).filter_by(request_id=3, name="NegativeDefault", default_value=-5).first()
    #     assert block is not None

    def test_set_block_default_value_not_specified(self, db_session):
        # Partition: No default_value specified
        your_instance = FuzzingService(db_session)
        your_instance.set_block(request_id=4, name="NoDefaultSpecified")
        block = db_session.query(Block).filter_by(request_id=4, name="NoDefaultSpecified", default_value=0).first()
        assert block is not None
        stmt = delete(Block).filter_by(request_id=1, name="ValidBlock4", default_value=42)
        db_session.execute(stmt)
        db_session.commit()