import pytest
from apis import auth_api,user_api
from utils import get_project_root, read_yaml


class TestUserSignOutLogin:

    @pytest.mark.smoke
    @pytest.mark.P0
    #负责用于测试 注册 登入 登出 功能
    def test_user_sign_out_login(context):
        # 读取登入测试数据
        js_param = read_yaml(get_project_root() / "data/test_data/user_login.yaml")
        login_result = auth_api.login(js_param)