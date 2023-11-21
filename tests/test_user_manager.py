import pytest
from fastapi.testclient import TestClient
from model.sql_model import User
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from main import app

client = TestClient(app)

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # 连接数据库
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
db = SessionLocal()


# pytest -s -p no:warnings tests/test_user_manager.py::TestFuzzManager::test_register
class TestFuzzManager:

    @pytest.fixture
    def delete_user(self):
        """
        通过 test 用户进行注册功能的测试，所以在测试之前需要确保数据库中不存在 test 这个用户。
        注意：test 用户不开放对外注册，仅用于系统内部测试
        :return:
        """
        db.query(User).filter(User.username == "test").delete()
        db.commit()

    def test_register(self, delete_user):
        """
        测试策略如下：
            1.正常输入
            2.输入非法邮箱
            3.输入过短用户名
            4.输入空的用户名
        :param delete_user:
        :return:
        """
        username, password, email = ("test", "mirror4s", "mirror4s@qq.com")
        # 正常注册一个用户
        register_data = {"username": username, "password": password, "email": email}
        res = client.post("/user/register", json=register_data)
        assert res.status_code == 200

        # 再次删除test用户以进行后续的测试
        delete_user

        register_data["email"] = "this is a test"
        res1 = client.post("/user/register", json=register_data)
        assert res1.status_code == 422

        # 用户名或密码长度不合规
        register_data["username"] = "123"
        assert client.post("/user/register", json=register_data).status_code == 422

        register_data["username"] = None
        assert client.post("/user/register", json=register_data).status_code == 422

    def test_login(self, delete_user):
        """
        测试策略如下：
            1.输入正确的账号密码
            2.输入不正确（不存在）的账号，密码随意
            3.输入正确的账号但是不正确的密码
            4.输入空的账号密码，fastapi 进行了封装，当字段为空时会响应字段缺失 422
        :return:
        """
        url = "/user/login"
        login_data = {
            "username": "admin",
            "password": "mirror4s"
        }
        res = client.post(url=url, data=login_data)
        assert res.status_code == 200
        assert "登录成功" in res.text

        login_data["username"] = "test"
        res = client.post(url=url, data=login_data)
        assert res.status_code == 404
        assert "用户不存在" in res.text

        login_data["password"] = "aaaaa"
        res = client.post(url=url, data=login_data)
        assert res.status_code == 404
        assert "密码错误" in res.text

        login_data["username"] = None
        res = client.post(url=url, data=login_data)
        assert res.status_code == 422
