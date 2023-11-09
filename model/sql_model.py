from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String, unique=True)
    role = Column(String)
    disabled = Column(Boolean)
    # 一个用户对应多个测试用例组
    test_case_groups = relationship("TestCaseGroup", back_populates="user")
    
    test_suites = relationship("TestSuite", back_populates="user")
    
    
class TestCaseGroup(Base):
    __tablename__ = 'test_case_groups'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    desc = Column(String, nullable=True)
    
    # 多个测试用例组对应一个用户
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="test_case_groups")
    
    # 一个测试用例组对应多个测试用例
    test_cases = relationship("FuzzyTestCase", back_populates="test_case_group")

class FuzzyTestCase(Base):
    __tablename__ = 'fuzzy_test_cases'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    desc = Column(String)
    
    # 多个测试用例对应一个测试用例组
    test_case_group_id = Column(Integer, ForeignKey('test_case_groups.id')) 
    test_case_group = relationship("TestCaseGroup", back_populates="test_cases")
    
    # 多个测试用例又对应一个测试套件
    test_suite_id = Column(Integer, ForeignKey('test_suites.id'), nullable=True)  # 测试套件 id
    test_suite = relationship("TestSuite", back_populates="test_cases")
    
    # 一个测试用例对应多个变量
    variables = relationship('Variable', back_populates="test_case")

class TestSuite(Base):
    __tablename__ = 'test_suites'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    desc = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="test_suites")
    test_cases = relationship("FuzzyTestCase", back_populates="test_suite")

class Variable(Base):
    __tablename__ = 'variables'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    default_value = Column(Integer, default=0)
    endian = Column(String)
    fuzzable = Column(Boolean, default=True)
    
    # 多个变量对应一个测试用例
    test_case_id = Column(Integer, ForeignKey('fuzzy_test_cases.id')) 
    test_case = relationship('FuzzyTestCase', back_populates="variables")
    
    # 自引用
    parent_id = Column(Integer, ForeignKey("variables.id"), nullable=True)
    children = relationship('Variable')
    

