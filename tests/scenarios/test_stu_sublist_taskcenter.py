"""
【场景测试】— 学生端 任务中心 & 学科列表
"""
import allure
import pytest
from common.assertion import AssertionEngine


@allure.epic("学生端")
@allure.feature("任务中心")

class TestStuCheckTaskCenter:
    @allure.story("查看任务中心列表")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    @pytest.mark.P1
    def test_stu_check_task_center(self, logged_in_student):
        """任务中心列表：接口成功，且 response 必须是列表"""
        resp = logged_in_student.post("/api/student/dashboard/task")
        ae = (AssertionEngine(resp)
              .status_code(200)
              .jsonpath_eq("$.code", 1)
              .has_field("response"))


class TestStuCheckEducationList:
    @allure.story("查看学科列表")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    @pytest.mark.P1
    def test_stu_check_education(self, logged_in_student):
        """学科列表：接口成功，且 response 必须是列表"""
        resp = logged_in_student.post("/api/student/education/subject/list")
        ae = (AssertionEngine(resp)
              .status_code(200)
              .jsonpath_eq("$.code", 1)
              .has_field("response"))