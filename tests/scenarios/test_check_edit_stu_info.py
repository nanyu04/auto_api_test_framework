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
        current_info_url = "/api/student/user/current"
        current_user_info = logged_in_student.get_user(current_info_url)
        AssertionEngine(current_user_info).status_code(200).has_field("message")



class TestUserEdit:
    @pytest.mark.P0
    @pytest.mark.smoke
    def test_user_edit(self, mock_server,logged_in_student):
        edit_data = read_yaml(get_project_root() / "data/test_data/stu_update_info.yaml")
        edit_url = edit_data[0]["url"]
        edit_json = edit_data[0]["request"]["json"]
        edit_user_request=logged_in_student.edit_user(edit_url,edit_json)
        AssertionEngine(edit_user_request).status_code(200)


