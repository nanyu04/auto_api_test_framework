import pytest
from apis import user_api
from common import logger, AssertionEngine
from config import settings
from utils import read_yaml, get_project_root
from framework.mock import MockProfile, MockResponse


class TestUserCheck:
    @pytest.mark.P0
    @pytest.mark.smoke
    def test_user_Check(self):
        login_data = read_yaml(get_project_root() / "data/test_data/user_login.yaml")
        login_url = login_data[0]["url"]
        login_json = login_data[0]["request"]["json"]
        login_res = user_api.login(login_url, login_json)
        logger.info("————————-登入完毕———————— ")
        # 进入修改用户步骤操作
        # 获取请求参数
        current_info_url = "/api/student/user/current"
        current_userinfo = user_api.get_user(current_info_url)


class TestUserEdit:
    @pytest.mark.P0
    @pytest.mark.smoke
    def test_user_edit(self, mock_server):
        # 注册这一块
        login_data = read_yaml(get_project_root() / "data/test_data/user_login.yaml")
        login_url = login_data[0]["url"]
        login_json = login_data[0]["request"]["json"]
        login_res = user_api.login(login_url, login_json)
        # 读取对应的url地址
        edit_data = read_yaml(get_project_root() / "data/test_data/user_edit_info.yaml")
        edit_url = edit_data[0]["url"]
        edit_json = edit_data[0]["request"]["json"]
        # 注册对应的profile
        register_mock_profile = MockProfile("用户编辑模块的mock测试")
        register_mock_profile.post(edit_url, MockResponse(status=201,
                                                          body="用户编辑成功成功成功mock模拟成功了",
                                                          headers={"Content-Type": "application/json"}))
        #开始启动mock服务
        start_mock=mock_server.load(register_mock_profile)
        #开始发送真实请求
        edit_user=user_api.edit_user(edit_url,edit_json)
        AssertionEngine(edit_user).status_code(201)

