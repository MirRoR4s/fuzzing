"""
sqlalchemy 数据库表
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String)
    role = Column(String)
    disabled = Column(Boolean)

    # 一个用户对应多个测试用例组
    fuzz_test_case_groups = relationship("FuzzTestCaseGroup", back_populates="user")
    # 一个用户对应多个测试套件
    fuzz_test_suites = relationship("FuzzTestSuite", back_populates="user")


class FuzzTestCaseGroup(Base):

    __tablename__ = "fuzz_test_case_groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    desc = Column(String, nullable=True)

    # 多个测试用例组对应一个用户
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="fuzz_test_case_groups")

    # 一个测试用例组对应多个测试用例
    fuzz_test_cases = relationship("FuzzTestCase", back_populates="fuzz_test_case_group")
    # 唯一约束，确保同一用户下用例组名称不重复
    __table_args__ = (UniqueConstraint('name', 'user_id'),)


class FuzzTestSuite(Base):
    
    __tablename__ = "fuzz_test_suites"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    desc = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="fuzz_test_suites")

    fuzz_test_cases = relationship("FuzzTestCase", back_populates="fuzz_test_suite")
    # 唯一约束，确保同一用户下测试套件名称不重复
    __table_args__ = (UniqueConstraint('name', 'user_id'),)


class FuzzTestCase(Base):
    
    __tablename__ = "fuzz_test_cases"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    desc = Column(String)

    # 多个测试用例对应一个测试用例组
    group_id = Column(Integer, ForeignKey("fuzz_test_case_groups.id"))
    fuzz_test_case_group = relationship("FuzzTestCaseGroup", back_populates="fuzz_test_cases")

    # 多个测试用例又对应一个测试套件
    suite_id = Column(Integer, ForeignKey("fuzz_test_suites.id"), nullable=True)
    fuzz_test_suite = relationship("FuzzTestSuite", back_populates="fuzz_test_cases")
    
    # 一个测试用例含有一个 Request 字段
    request = relationship("Request", uselist=False, back_populates="fuzz_test_case")
    
    __table_args__ = (UniqueConstraint('name', 'group_id'),)



class Request(Base):

    __tablename__ = "request"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # 外键是模糊测试用例 id
    case_id = Column(Integer, ForeignKey("fuzz_test_cases.id"))
    fuzz_test_case = relationship("FuzzTestCase", back_populates="request")

    # Request 字段可含有其它的字段
    block = relationship("Block", back_populates="request")
    
    # byte = relationship("Byte", back_populates="request")
    
    # bytes = relationship("Bytes", back_populates="request")

    static = relationship("Block", back_populates="request")
    
class Block(Base):

    __tablename__ = "block"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    default_value = Column(Integer, default=0)

    # 外键是 Request id
    request_id = Column(Integer, ForeignKey("request.id"))
    request = relationship("Request", back_populates="block")

    # byte = relationship("Byte", back_populates="block")
    # bytes = relationship("Bytes", back_populates="block")
    static = relationship("Block", back_populates="block")

class Static(Base):
    """static 表原型
    有两个唯一性约束：request id + name 以及 block id + name
    """
    __tablename__ = "static"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    default_value = Column(Integer, default=0)
    request_id = Column(Integer, ForeignKey("request.id"))
    block_id = Column(Integer, ForeignKey("block.id"))

    __table_args__ = (UniqueConstraint('name', 'request_id'), UniqueConstraint('name', 'block_id'))
    

# class Byte(Base):

#     __tablename__ = "byte"
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     default_value = Column(Integer, default=0)
#     max_num = Column(Integer, nullable=True)
#     endian = Column(String, default=">")
#     output_format = Column(String, default="binary")
#     signed = Column(Boolean, default=False)
#     full_range = Column(Boolean, default=False)
#     fuzz_values = Column(JSON, nullable=True)
#     fuzzable = Column(Boolean, default=True)

#     # 外键是 Request id
#     request_id = Column(Integer, ForeignKey("request.id"), nullable=True)
#     request = relationship("RequestField", back_populates="byte")

#     # Byte 字段可能是 Block 字段的子字段
#     block_id = Column(Integer, ForeignKey("block_fields.id"), nullable=True)
#     block = relationship("BlockField", back_populates="byte")


# class Bytes(Base):

#     __tablename__ = "bytes"
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     default_value = Column(Integer, default=0)
#     size = Column(Integer, nullable=True)
#     padding = Column(String)
#     max_len = Column(Integer, nullable=True)
#     fuzzable = Column(Boolean, default=True)

#     # 外键是 Request id
#     request_id = Column(Integer, ForeignKey("requests.id"))
#     request = relationship("RequestField", back_populates="bytes")

#     # Byte 字段可能是 Block 字段的子字段
#     block_id = Column(Integer, ForeignKey("blocks.id"), nullable=True)
#     block = relationship("BlockField", back_populates="bytes")
