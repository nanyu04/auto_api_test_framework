import pytest
from apis import user_api
from common import logger
from config import settings
from utils import read_yaml, get_project_root


class TestUserEdit:
    @pytest.mark.P0
    @pytest.mark.smoke
    def test_user_edit(self):
        login_data = read_yaml(get_project_root()/ "data/test_data/user_login.yaml")
        login_url = login_data[1]["url"]
        login_json = login_data[1]["request"]["json"]
        login_res = user_api.login(login_url, login_json)
        logger.info("————————-登入完毕————————  ")
        # 进入修改用户步骤操作
