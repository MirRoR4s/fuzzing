import pytest
import json
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from services.sql_model import FuzzTestCaseGroup
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
        
    @pytest.fixture
    def add_fuzz_test_case_group(self, token):
        group_name = "test"
        client.get(f"/fuzz/test/create/group?{group_name}", headers=token)
    
    @pytest.fixture
    def add_fuzz_test_case(self, token):
        case_name = "test"
        client.get(f"/fuzz/test/create/case?{case_name}", headers=token)

    def test_create_fuzzing_group(self, token):
        """
        测试策略如下：
            1.组名长度：1-20，20，> 20

            2.组名重复：创建 test 后继续创建 test

            3.组名为空或零：fastapi进行了封装，会返回 422


        """
        prefix = "/fuzz/create/group?group_name="
        group_name = "test"
        res = client.get(url=f"{prefix}{group_name}", headers=token)
        print(res.text)
        assert res.status_code == 200
        assert "创建成功" in res.text

        # 组名重复
        res = client.get(url=f"{prefix}{group_name}", headers=token)
        assert res.status_code == 422
        assert "组名重复" in res.text

        # 组名过长
        group_name = "test" * 20
        res = client.get(url=f"{prefix}{group_name}", headers=token)
        assert res.status_code == 422
        assert "组名过长" in res.text

        # 系统内部组名
        group_name = "test"
        res = client.get(url=f"{prefix}{group_name}", headers=token)
        assert res.status_code == 422
        assert "系统内部" in res.text

    def test_create_fuzzing_case(self, token):
        header_token = token
        res = client.get("/fuzz/create/fuzzing/case", headers=header_token)
        print(res)

    def test_set_block(self, token):
        pass

    def test_set_static(self, token):
        
        req_data = ""
        res = client.get("/fuzz/test/set/static?")

