from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String)
    role = Column(String)
    disabled = Column(Boolean)
    test_case_groups = relationship("TestCaseGroup", back_populates="user")
    test_suites = relationship("TestSuite", back_populates="user")
    

class TestCaseGroup(Base):
    __tablename__ = 'test_case_groups'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="test_case_groups")
    test_cases = relationship("FuzzyTestCase", back_populates="test_case_group")

class TestSuite(Base):
    __tablename__ = 'test_suites'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="test_suites")
    test_cases = relationship("FuzzyTestCase", back_populates="test_suite")

class FuzzyTestCase(Base):
    __tablename__ = 'fuzzy_test_cases'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    test_case_id = Column(String, unique=True, index=True)  # 测试用例的唯一标识符
    desc = Column(String)
    size = Column(Integer)
    unit = Column(String)
    default_value = Column(String)
    endian = Column(String)
    fuzzable = Column(Boolean, default=True)
    parent_id = Column(Integer, ForeignKey('fuzzy_test_cases.id'), nullable=True)
    test_case_group_id = Column(Integer, ForeignKey('test_case_groups.id'))
    test_case_group = relationship("TestCaseGroup", back_populates="test_cases")
    test_suite_id = Column(Integer, ForeignKey('test_suites.id'))
    test_suite = relationship("TestSuite", back_populates="test_cases")
    parent = relationship("FuzzyTestCase", backref="children", remote_side=id, uselist=False)

