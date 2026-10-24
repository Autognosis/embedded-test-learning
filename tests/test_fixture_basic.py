import pytest


# 1. return 型：只提供数据，无清理
# 换行后输出"[setup] 准备 user_data" 然后返回{"name": "Alice", "role": "admin"}
@pytest.fixture
def user_data():
    print("\n[setup] 准备 user_data")
    return {"name": "Alice", "role": "admin"}


# 2. yield 型：有 setup 和 teardown
# 创建一个临时文件，向其写入数据，然后清理
@pytest.fixture
def temp_file(tmp_path):
    print("\n[setup] 创建临时文件")
    file = tmp_path / "data.txt"
    file.write_text("Hello Pytest-Fixture", encoding="utf-8")
    yield file
    print("\n[teardown] 删除临时文件")
    file.unlink(missing_ok=True)


# 3. fixture 依赖 fixture
@pytest.fixture
def user_service(user_data):
    print("\n[setup] 用 user_data 构造 service")

    class UserService:
        def __init__(self, data):
            self.data = data

        def get_role(self):
            return self.data["role"]

    return UserService(user_data)


# 4. module scope：整个模块只创建一次
@pytest.fixture(scope="module")
def module_config():
    print("\n[setup] module_config 创建（整个模块只一次）")
    return {"env": "test"}


def test_user_data(user_data):
    assert user_data["role"] == "admin"


def test_tmp_file(temp_file):
    assert temp_file.read_text(encoding="utf-8") == "Hello Pytest-Fixture"


def test_user_service(user_service):
    assert user_service.get_role() == "admin"


def test_module_config1(module_config):
    assert module_config["env"] == "test"


def test_module_config2(module_config):
    assert module_config["env"] == "test"
