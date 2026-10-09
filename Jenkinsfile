pipeline {
    agent any

    parameters {
        choice(
            name: 'ENV',
            choices: ['dev', 'test', 'staging', 'prod'],
            description: '选择测试环境'
        )
        choice(
            name: 'TEST_LEVEL',
            choices: ['smoke', 'regression', 'all'],
            description: '选择测试范围'
        )
        string(
            name: 'MARKER',
            defaultValue: '',
            description: '自定义 marker，如 P0 或留空'
        )
        booleanParam(
            name: 'MOCK_MODE',
            defaultValue: false,
            description: '启用 Mock 模式（不依赖外部服务）'
        )
    }

    environment {
        PYTHONUNBUFFERED = "1"
        REPORTS_DIR = "${WORKSPACE}/reports/allure"
        FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/91e4d0a5-ed8c-4393-ab8a-2f1e8d631954"
        JOB_NAME = "${env.JOB_NAME}"
        BUILD_NUMBER = "${env.BUILD_NUMBER}"
        BUILD_URL = "${env.BUILD_URL}"
    }

    stages {
        stage("Checkout") {
            steps {
                checkout scm
            }
        }

        stage("Setup Python") {
            steps {
                sh """
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip -q
                    pip install -r requirements.txt -q
                """
            }
        }

        stage("Prepare Config") {
            steps {
                script {
                    def envFile = ".env.${params.ENV}"
                    if (fileExists(envFile)) {
                        sh "cp ${envFile} .env"
                    }
                }
            }
        }

        stage("Run Tests") {
            steps {
                script {
                    def args = []
                    if (params.TEST_LEVEL == "smoke") {
                        args << "-m" << "smoke"
                    } else if (params.TEST_LEVEL == "regression") {
                        args << "-m" << "regression"
                    }
                    if (params.MARKER) {
                        args << "-m" << params.MARKER
                    }
                    if (params.MOCK_MODE) {
                        args << "--mode=mock"
                    }
                    args << "--alluredir" << "${REPORTS_DIR}"
                    args << "-n" << "auto"
                    args << "--timeout=60"

                    sh """
                        . .venv/bin/activate
                        pytest ${args.join(" ")} tests/
                    """
                }
            }
        }
    }

    post {
        always {
            script {
                allure includeProperties: false,
                       results: [[path: "${REPORTS_DIR}"]]

                // 读取测试结果
                def total = 0
                def passed = 0
                def failed = 0
                def skipped = 0

                try {
                    // 从 JUnit/xUnit 格式的测试结果中获取统计
                    // 也可通过 allure 命令行工具获取
                    def resultFile = findFiles(glob: "${REPORTS_DIR}/**/*-result.json")
                    echo "找到 ${resultFile.size()} 个测试结果文件"
                } catch (err) {
                    echo "无法读取测试结果: ${err}"
                }
            }

            // 发送飞书通知
            script {
                def status = currentBuild.result ?: "SUCCESS"
                def statusIcon = status == "SUCCESS" ? "✅" : "❌"
                def duration = currentBuild.durationString ?: ""
                def testSummary = ""

                // 从 allure 报告目录中提取测试统计
                try {
                    def summaryFile = "${REPORTS_DIR}/export/statistics.json"
                    if (fileExists(summaryFile)) {
                        def summary = readJSON file: summaryFile
                        def total = summary.statistic.total ?: 0
                        def passed = summary.statistic.passed ?: 0
                        def failed = summary.statistic.failed ?: 0
                        def skipped = summary.statistic.skipped ?: 0
                        testSummary = "通过: ${passed} | 失败: ${failed} | 跳过: ${skipped} | 总计: ${total}"
                    }
                } catch (err) {
                    testSummary = "测试执行完成"
                }

                def message = """{
                    "msg_type": "interactive",
                    "card": {
                        "header": {
                            "title": {
                                "tag": "plain_text",
                                "content": "${statusIcon} API 自动化测试 ${status}"
                            },
                            "template": "${status == "SUCCESS" ? "green" : "red"}"
                        },
                        "elements": [
                            {
                                "tag": "div",
                                "text": {
                                    "tag": "lark_md",
                                    "content": "**环境**: ${params.ENV}\\n**范围**: ${params.TEST_LEVEL}\\n**Mock**: ${params.MOCK_MODE}\\n${testSummary ? "**结果**: ${testSummary}" : ""}\\n**耗时**: ${duration}"
                                }
                            },
                            {
                                "tag": "hr"
                            },
                            {
                                "tag": "div",
                                "text": {
                                    "tag": "lark_md",
                                    "content": "**任务**: ${JOB_NAME}\\n**构建**: #${BUILD_NUMBER}"
                                }
                            },
                            {
                                "tag": "action",
                                "actions": [
                                    {
                                        "tag": "button",
                                        "text": {
                                            "tag": "plain_text",
                                            "content": "查看报告"
                                        },
                                        "type": "link",
                                        "url": "${BUILD_URL}allure"
                                    },
                                    {
                                        "tag": "button",
                                        "text": {
                                            "tag": "plain_text",
                                            "content": "查看控制台"
                                        },
                                        "type": "link",
                                        "url": "${BUILD_URL}console"
                                    }
                                ]
                            }
                        ]
                    }
                }"""

                sh """
                    curl -s -X POST "${FEISHU_WEBHOOK}" \
                        -H "Content-Type: application/json" \
                        -d '${message}'
                """
            }
        }
    }
}
