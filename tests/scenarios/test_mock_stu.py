import pytest

from apis import user_api
from common import AssertionEngine
from framework import MockProfile
from framework.mock import MockResponse
from utils import read_yaml, get_project_root


class TestMockStuEdit:
    @pytest.mark.smoke
    @pytest.mark.P0
    def test_mock_stu_edit(self, mock_server, logged_in_student):
        edit_data = read_yaml(get_project_root() / "data/test_data/stu_update_info.yaml")
        edit_url = edit_data[0]["url"]
        edit_json = edit_data[0]["request"]["json"]
        register_mock_edit_profile = MockProfile("用户编辑模块的mock测试")
        register_mock_edit_profile.post(edit_url, MockResponse(status=201,
                                                               body="用户编辑成功成功成功mock模拟成功了 通过了mock模拟测试",
                                                               headers={"Content-Type": "application/json"}))
        load_mock = mock_server.load(register_mock_edit_profile)
        edit_user = logged_in_student.edit_user(edit_url, edit_json)
        AssertionEngine(edit_user).status_code(201)


class TestMockStuTpaper:
    @pytest.mark.smoke
    @pytest.mark.P0
    def test_mock_stu_tpaper(self, mock_server, logged_in_student):
        tpaper_url = "/api/student/exampaper/answer/read/4"
        register_mock_Tpaper_profile = MockProfile("用户查询试卷模块的mock测试")
        register_mock_Tpaper_profile.post(tpaper_url, MockResponse(status=200,
                                                                   body="你没有考试试卷，你已经全部满分通过了",
                                                                   headers={"Content-Type": "application/json"}))
        load_mock = mock_server.load(register_mock_Tpaper_profile)
        res_result = logged_in_student.get_user(tpaper_url)
        AssertionEngine(res_result).status_code(200)


class TestMockStuTpaperSub:
    @pytest.mark.smoke
    @pytest.mark.P0
    def test_mock_stu_tpaper_sub(self, mock_server, logged_in_student):
        TaperSub_data = read_yaml(get_project_root() / "data/test_data/stu_testpaper_submit.yaml")
        Tapersub_url = TaperSub_data[0]["url"]
        Tapersub_json = TaperSub_data[0]["request"]["json"]
        register_mock_TaperSub = MockProfile("用户提交试卷模块的mock测试")
        register_mock_TaperSub.post(Tapersub_url, MockResponse(status=201,
                                                               body="你提交失败因为你的成绩不合格",
                                                               headers={"Content-Type": "application/json"}))
        load_mock = mock_server.load(register_mock_TaperSub)
        res_result = logged_in_student.post(path=Tapersub_url, json=Tapersub_json)
        AssertionEngine(res_result).status_code(201)
