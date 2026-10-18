"""
【Mock 测试】— 学生模块 Mock 验证

每个用例注册 → 执行 → 验证请求参数 → 自动清理，不污染其他用例。
"""
import allure
import pytest
from apis import user_api
from common import AssertionEngine
from framework import MockProfile
from framework.mock import MockResponse
from utils import read_yaml, get_project_root


class TestMockStuEdit:
    """Mock 学生编辑个人信息"""

    @allure.epic("Mock测试")
    @allure.feature("学生编辑")
    @allure.story("Mock模拟学生编辑个人信息")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    @pytest.mark.P0
    def test_mock_stu_edit(self, mock_session, logged_in_student):
        """Mock 拦截编辑接口 → 验证请求参数正确发出"""
        edit_data = read_yaml(get_project_root() / "data/test_data/stu_update_info.yaml")
        edit_url = edit_data[0]["url"]
        edit_json = edit_data[0]["request"]["json"]

        profile = MockProfile("学生编辑Mock")
        profile.post(edit_url, MockResponse(status=201,
                                            body={"code": 1, "message": "Mock模拟成功"},
                                            headers={"Content-Type": "application/json"}))
        mock_session.load(profile)

        resp = logged_in_student.edit_user(edit_url, edit_json)
        AssertionEngine(resp).status_code(201)

        # 验证请求参数正确发出（不"自证"）
        last_req = mock_session.last_request
        assert last_req is not None, "Mock 没有被命中——请求可能没发出去"
        req_body = last_req.json()
        assert req_body["id"] == edit_json["id"], (
            f"请求体 id 不正确: 期望 {edit_json['id']}, 实际 {req_body.get('id')}"
        )
        assert req_body["userName"] == edit_json["userName"], (
            f"请求体 userName 不正确: 期望 {edit_json['userName']}, 实际 {req_body.get('userName')}"
        )


class TestMockStuTpaper:
    """Mock 学生查询试卷"""

    @allure.epic("Mock测试")
    @allure.feature("试卷查询")
    @allure.story("Mock模拟学生查询试卷")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    @pytest.mark.P0
    def test_mock_stu_tpaper(self, mock_session, logged_in_student):
        """Mock 拦截试卷查询 → 验证 method + URL 正确"""
        tpaper_url = "/api/student/exampaper/answer/read/4"

        profile = MockProfile("试卷查询Mock")
        profile.post(tpaper_url, MockResponse(status=200,
                                              body={"code": 1, "message": "试卷Mock成功"},
                                              headers={"Content-Type": "application/json"}))
        mock_session.load(profile)

        resp = logged_in_student.get_user(tpaper_url)
        AssertionEngine(resp).status_code(200)

        # 验证请求被正确拦截
        last_req = mock_session.last_request
        assert last_req is not None, "Mock 没有被命中"
        assert last_req.method == "POST", f"期望 POST, 实际 {last_req.method}"
        assert tpaper_url in last_req.url, f"URL 不匹配: {last_req.url}"


class TestMockStuTpaperSub:
    """Mock 学生提交试卷"""

    @allure.epic("Mock测试")
    @allure.feature("试卷提交")
    @allure.story("Mock模拟学生提交试卷")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    @pytest.mark.P0
    def test_mock_stu_tpaper_sub(self, mock_session, logged_in_student):
        """Mock 拦截试卷提交 → 验证请求体参数正确"""
        sub_data = read_yaml(get_project_root() / "data/test_data/stu_testpaper_submit.yaml")
        sub_url = sub_data[0]["url"]
        sub_json = sub_data[0]["request"]["json"]

        profile = MockProfile("提交试卷Mock")
        profile.post(sub_url, MockResponse(status=201,
                                           body={"code": 1, "message": "提交Mock成功"},
                                           headers={"Content-Type": "application/json"}))
        mock_session.load(profile)

        resp = logged_in_student.post(path=sub_url, json=sub_json)
        AssertionEngine(resp).status_code(201)

        # 验证请求参数
        last_req = mock_session.last_request
        assert last_req is not None, "Mock 没有被命中"
        req_body = last_req.json()
        assert req_body.get("id") == sub_json["id"], (
            f"请求体 id 不正确: 期望 {sub_json['id']}, 实际 {req_body.get('id')}"
        )