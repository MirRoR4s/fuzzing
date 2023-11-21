import pytest
import json
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from model.sql_model import FuzzTestCaseGroup
from fastapi.testclient import TestClient

client = TestClient(app)

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # 连接数据库
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
db = SessionLocal()


class TestFuzzManager:

    @pytest.fixture
    def token(self):
        data = {
            "username": "admin",
            "password": "mirror4s"
        }
        token = json.loads(client.post(url="/user/login", data=data).text)['access_token']
        print(token)
        yield {"Authorization": "Bearer " + token}

    @pytest.fixture
    def delete_group(self):
        db.query(FuzzTestCaseGroup).filter(FuzzTestCaseGroup.name == "test").delete()
        db.commit()
        db.close()

    def test_create_fuzzing_group(self, token, delete_group):
        """
        测试策略如下：
            1.组名长度：0，1-20，20，> 20

            2.组名重复：创建 test 后继续创建 test

            3.组名为空：fastapi进行了封装，会返回 422

            注意：名为test的用例组不对外开放，仅由系统内部测试所用，所以不允许用户创建一个名为 test 的用例组
        """
        prefix = "/fuzz/create/group"
        group_name = ""
        res = client.get(url=f"{prefix}{group_name}", headers=token)
        assert res.status_code == 422
        assert "组名长度为零" in res.text

        assert client.get(url=f"{prefix}{group_name}", headers=token).status_code == 422

        group_name = "test"
        assert client.get(url=f"{prefix}{group_name}", headers=token).status_code == 200

        group_name = "test" * 20
        assert client.get(url=f"{prefix}{group_name}", headers=token).status_code == 422

        group_name = "test"
        res = client.get(url=f"{prefix}{group_name}", headers=token)
        assert res.status_code == 422
        assert "组名重复" in res.text


    def test_create_fuzzing_case(self, token):
        header_token = token
        res = client.get("/fuzz/create/fuzzing/case", headers=header_token)
        print(res)

    def test_set_block(self, token):
        pass
