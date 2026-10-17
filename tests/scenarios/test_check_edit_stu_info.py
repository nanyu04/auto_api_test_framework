import pytest
from apis import user_api
from common import logger, AssertionEngine
from config import settings
from utils import read_yaml, get_project_root
from framework.mock import MockProfile, MockResponse


class TestUserCheck:
    @pytest.mark.P0
    @pytest.mark.smoke
    def test_user_Check(self,logged_in_student):
        logger.info("————————-登入完毕———————— ")
        # 进入修改用户步骤操作
        # 获取请求参数
        current_info_url = "/api/student/user/current"
        current_user_info = logged_in_student.get_user(current_info_url)
        #用于鉴权断言
        AssertionEngine(current_user_info).status_code(200).has_field("message")



class TestUserEdit:
    @pytest.mark.P0
    @pytest.mark.smoke
    def test_user_edit(self, mock_server,logged_in_student):
        #登入已经被logged_in_student给完成了 直接就是成功登入成功 user_api
        # 读取对应的url地址
        edit_data = read_yaml(get_project_root() / "data/test_data/stu_update_info.yaml")
        edit_url = edit_data[0]["url"]
        edit_json = edit_data[0]["request"]["json"]
        #直接进行发送真实请求
        edit_user_request=logged_in_student.edit_user(edit_url,edit_json)
        AssertionEngine(edit_user_request).status_code(200)


