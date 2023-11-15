"""
sqlalchemy 数据库表
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    """
    User _summary_

    :param Base: _description_
    :type Base: _type_
    """

    __tablename__ = "users"
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
    """
    TestCaseGroup _summary_

    :param Base: _description_
    :type Base: _type_
    """

    __tablename__ = "test_case_groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    desc = Column(String, nullable=True)

    # 多个测试用例组对应一个用户
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="test_case_groups")

    # 一个测试用例组对应多个测试用例
    test_cases = relationship("FuzzyTestCase", back_populates="test_case_group")


class FuzzyTestCase(Base):
    """
    FuzzyTestCase _summary_

    :param Base: _description_
    :type Base: _type_
    """

    __tablename__ = "fuzzy_test_cases"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    desc = Column(String)

    # 多个测试用例对应一个测试用例组
    test_case_group_id = Column(Integer, ForeignKey("test_case_groups.id"))
    test_case_group = relationship("TestCaseGroup", back_populates="test_cases")

    # 多个测试用例又对应一个测试套件
    test_suite_id = Column(Integer, ForeignKey("test_suites.id"), nullable=True)
    # 测试套件 id
    test_suite = relationship("TestSuite", back_populates="test_cases")

    attributes = relationship("Attribute", back_populates="test_case")

    # 一个测试用例含有一个 Request 字段
    request_field = relationship(
        "RequestField", uselist=False, back_populates="fuzzing_case"
    )


class TestSuite(Base):
    """
    TestSuite _summary_

    :param Base: _description_
    :type Base: _type_
    """

    __tablename__ = "test_suites"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    desc = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="test_suites")

    test_cases = relationship("FuzzyTestCase", back_populates="test_suite")


class Attribute(Base):
    """
    Attribute _summary_

    :param Base: _description_
    :type Base: _type_
    """

    __tablename__ = "attributes"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    default_value = Column(Integer, default=0)
    endian = Column(String)
    fuzzable = Column(Boolean, default=True)

    # 多个属性对应一个测试用例
    test_case_id = Column(Integer, ForeignKey("fuzzy_test_cases.id"))
    test_case = relationship("FuzzyTestCase", back_populates="attributes")


class RequestField(Base):
    """
    RequestField _summary_

    :param Base: _description_
    :type Base: _type_
    """

    __tablename__ = "request_fields"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # 外键是模糊测试用例 id
    fuzzing_case_id = Column(Integer, ForeignKey("fuzzy_test_cases.id"))
    fuzzing_case = relationship("FuzzyTestCase", back_populates="request_field")

    # Request 字段可含有其它的字段
    block_children = relationship("BlockField", back_populates="request")
    byte_children = relationship("ByteField", back_populates="request")
    bytes_children = relationship("BytesField", back_populates="request")


class BlockField(Base):
    """
    BlockField _summary_

    :param Base: _description_
    :type Base: _type_
    """

    __tablename__ = "block_fields"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    default_value = Column(Integer, default=0)

    # 外键是 Request id
    request_id = Column(Integer, ForeignKey("request_fields.id"))
    request = relationship("RequestField", back_populates="block_children")
    
    byte_children = relationship("ByteField", back_populates="block")
    bytes_children = relationship("BytesField", back_populates="block")


class ByteField(Base):
    """
    ByteField _summary_

    :param Base: _description_
    :type Base: _type_
    """

    __tablename__ = "byte_fields"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    default_value = Column(Integer, default=0)
    max_num = Column(Integer, nullable=True)
    endian = Column(String, default=">")
    output_format = Column(String, default="binary")
    signed = Column(Boolean, default=False)
    full_range = Column(Boolean, default=False)
    fuzz_values = Column(JSON, nullable=True)
    fuzzable = Column(Boolean, default=True)

    # 外键是 Request id
    request_id = Column(Integer, ForeignKey("request_fields.id"), nullable=True)
    request = relationship("RequestField", back_populates="byte_children")
    
    # Byte 字段可能是 Block 字段的子字段
    block_id = Column(Integer, ForeignKey("block_fields.id"), nullable=True)
    block = relationship("BlockField", back_populates="byte_children")

class BytesField(Base):
    """
    BytesField _summary_

    :param Base: _description_
    :type Base: _type_
    """

    __tablename__ = "bytes_fields"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    default_value = Column(Integer, default=0)
    size = Column(Integer, nullable=True)
    padding = Column(String)
    max_len = Column(Integer, nullable=True)
    fuzzable = Column(Boolean, default=True)

    # 外键是 Request id
    request_id = Column(Integer, ForeignKey("request_fields.id"))
    request = relationship("RequestField", back_populates="bytes_children")
    

    # Byte 字段可能是 Block 字段的子字段
    block_id = Column(Integer, ForeignKey("block_fields.id"), nullable=True)
    block = relationship("BlockField", back_populates="bytes_children")
