// ============================================================
//  飞书通知函数（必须放在 pipeline 块外面）
// ============================================================
def feishuNotify(status, summary) {
    def colorMap = [
        'SUCCESS': 'green',
        'FAILURE': 'red',
        'UNSTABLE': 'yellow',
        'ABORTED': 'grey',
    ]
    def titleMap = [
        'SUCCESS': '✅ 构建成功',
        'FAILURE': '❌ 构建失败',
        'UNSTABLE': '⚠️ 构建不稳定',
        'ABORTED': '⏹ 构建已取消',
    ]
    def color = colorMap.get(status, 'red')
    def title = titleMap.get(status, '构建通知')

    // 安全获取构建信息
    def branchName = env.BRANCH_NAME ?: env.GIT_BRANCH ?: 'unknown'
    def buildTime = currentBuild.startTimeInMillis
        ? new Date(currentBuild.startTimeInMillis).format('yyyy-MM-dd HH:mm:ss')
        : 'N/A'
    def duration = currentBuild.durationString?.replace(' and counting', '') ?: 'N/A'

    def cardJson = """{
    "msg_type": "interactive",
    "card": {
        "config": { "wide_screen_mode": true },
        "header": {
            "title": { "tag": "plain_text", "content": "${title} — ${env.PROJECT_NAME}" },
            "template": "${color}"
        },
        "elements": [
            {
                "tag": "div",
                "fields": [
                    { "is_short": true, "text": { "tag": "lark_md", "content": "**🆔 构建编号**\\n${env.BUILD_NUMBER}" } },
                    { "is_short": true, "text": { "tag": "lark_md", "content": "**🌿 分支**\\n${branchName}" } },
                    { "is_short": true, "text": { "tag": "lark_md", "content": "**🔧 环境**\\n${params.ENV}" } },
                    { "is_short": true, "text": { "tag": "lark_md", "content": "**📊 测试范围**\\n${params.TEST_LEVEL}" } }
                ]
            },
            { "tag": "hr" },
            {
                "tag": "div",
                "fields": [
                    { "is_short": true, "text": { "tag": "lark_md", "content": "**📅 时间**\\n${buildTime}" } },
                    { "is_short": true, "text": { "tag": "lark_md", "content": "**⏱ 耗时**\\n${duration}" } }
                ]
            },
            { "tag": "hr" },
            {
                "tag": "div",
                "text": { "tag": "lark_md", "content": "${summary}" }
            },
            { "tag": "hr" },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": { "tag": "plain_text", "content": "🔗 查看构建" },
                        "type": "primary",
                        "multi_url": { "url": "${env.BUILD_URL}", "android_url": "", "ios_url": "", "pc_url": "" }
                    },
                    {
                        "tag": "button",
                        "text": { "tag": "plain_text", "content": "📊 Allure 报告" },
                        "type": "default",
                        "multi_url": { "url": "${env.BUILD_URL}allure", "android_url": "", "ios_url": "", "pc_url": "" }
                    }
                ]
            }
        ]
    }
}"""

    powershell """
        try {
            \$body = @'
${cardJson}
'@
            \$response = Invoke-RestMethod -Uri ${env.FEISHU_URL} -Method Post -ContentType "application/json" -Body \$body
            if (\$response.code -ne 0) {
                Write-Warning "飞书通知返回异常: \$(\$response | ConvertTo-Json -Compress)"
            } else {
                Write-Host "飞书通知发送成功 (status=${status})"
            }
        } catch {
            Write-Warning "飞书通知发送失败: \$(\$_ | Out-String)"
        }
    """
}

// ============================================================
//  pipeline 声明式流水线
// ============================================================
pipeline {
    agent any

    tools {
        jdk "jdk8"
    }

    options {
        timestamps()
        timeout(time: 60, unit: "MINUTES")
        buildDiscarder(logRotator(numToKeepStr: "20"))
        disableConcurrentBuilds()
    }

    parameters {
        choice(name: 'ENV', choices: ['dev','test','staging','prod'], description: '选择测试环境')
        choice(name: 'TEST_LEVEL', choices: ['smoke','regression','all'], description: '测试范围')
        string(name: 'MARKER', defaultValue: '', description: '自定义 pytest marker')
        booleanParam(name: 'MOCK_MODE', defaultValue: false, description: '启用 Mock 模式')
    }

    environment {
        REPORTS_DIR   = 'reports/allure'
        FEISHU_URL    = 'https://open.feishu.cn/open-apis/bot/v2/hook/91e4d0a5-ed8c-4393-ab8a-2f1e8d631954'
        PROJECT_NAME  = 'API 接口自动化测试'
        VENV_DIR      = 'venv'                         // 工作空间内，用完即删
        PIP_CACHE_DIR = 'D:\\jenkins\\pip-cache'       // 持久化，跨构建复用
    }

    stages {
        stage('① 拉取代码') {
            steps { checkout scm }
        }

        stage('② 环境准备') {
            steps {
                script {
                    // ① 检查 python 是否被 WindowsApps 劫持（常见卡住原因）
                    def pythonPath = bat(
                        returnStdout: true,
                        script: "where python"
                    ).trim().readLines().first()
                    echo "🔍 使用的 Python: ${pythonPath}"
                    if (pythonPath.contains('WindowsApps')) {
                        error "Python 被 WindowsApps 占位符劫持！请将 Python 安装路径移到 WindowsApps 前面"
                    }

                    echo "🔄 创建虚拟环境..."
                    bat """
                        if exist "${env.VENV_DIR}" rmdir /s /q "${env.VENV_DIR}"
                        if not exist "${env.PIP_CACHE_DIR}" mkdir "${env.PIP_CACHE_DIR}"
                        python -m venv --without-pip "${env.VENV_DIR}"
                    """

                    echo "📦 安装 pip 和依赖..."
                    bat """
                        call "${env.VENV_DIR}\\Scripts\\activate.bat"
                        python -m ensurepip --upgrade
                        python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple -q
                        pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple -q --cache-dir "${env.PIP_CACHE_DIR}"
                    """

                    echo "✅ 环境准备完成"
                }
            }
        }

        stage('③ 加载配置') {
            steps {
                script {
                    def envFile = ".env.${params.ENV}"
                    if (fileExists(envFile)) {
                        bat "copy /Y ${envFile} .env"
                        echo "✅ 已加载配置: ${envFile}"
                    } else {
                        echo "⚠ 未找到 ${envFile}，跳过"
                    }
                }
            }
        }

        stage('④ 执行测试') {
            steps {
                script {
                    // 先清理上次的报告
                    bat "if exist ${env.REPORTS_DIR} rmdir /S /Q ${env.REPORTS_DIR}"

                    def args = []
                    if (params.TEST_LEVEL == 'smoke') {
                        args << '-m' << 'smoke'
                    }
                    if (params.MARKER?.trim()) {
                        args << '-m' << params.MARKER.trim()
                    }
                    if (params.MOCK_MODE) {
                        args << '--mode=mock'
                    }
                    args << '--alluredir' << env.REPORTS_DIR
                    args << '-v'
                    args << '--junitxml=reports/junit.xml'
                    args << 'tests/'
                    args << '--timeout=60'

                    echo "⏳ 执行: pytest ${args.join(' ')}"

                    // 捕获 pytest 退出码但不中断流水线
                    try {
                        def venvActivate = "call \"${env.VENV_DIR}\\Scripts\\activate.bat\""
                        bat "${venvActivate} && pytest ${args.join(' ')}"
                    } catch (Exception e) {
                        echo "⚠ pytest 返回了非零退出码（有失败用例），继续执行..."
                    }
                }
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: "reports/junit.xml"
            script {
                try {
                    allure results: [[path: env.REPORTS_DIR]]
                } catch (Exception e) {
                    echo "⚠ Allure 报告发布失败: ${e.message}"
                }
            }
            // 清理工作空间，虚拟环境用完即删
            bat '''
                if exist venv rmdir /s /q venv
                if exist .pytest_cache rmdir /s /q .pytest_cache
                if exist reports rmdir /s /q reports
                for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
                exit /b 0
            '''
        }

        success {
            script {
                def msg = "✅ **全部测试通过**"
                if (params.MOCK_MODE) { msg += "\\n\\n**Mock 模式**: 开启" }
                if (params.MARKER?.trim()) { msg += "\\n**自定义 Marker**: ${params.MARKER.trim()}" }
                feishuNotify('SUCCESS', msg)
            }
        }

        failure {
            script {
                def msg = "⚠️ **存在失败用例，请及时处理**"
                msg += "\\n\\n**Mock 模式**: ${params.MOCK_MODE ? '开启' : '关闭'}"
                if (params.MARKER?.trim()) { msg += "\\n**自定义 Marker**: ${params.MARKER.trim()}" }
                feishuNotify('FAILURE', msg)
            }
        }

        unstable {
            script {
                def msg = "⚠️ **测试结果不稳定**"
                msg += "\\n\\n**Mock 模式**: ${params.MOCK_MODE ? '开启' : '关闭'}"
                if (params.MARKER?.trim()) { msg += "\\n**自定义 Marker**: ${params.MARKER.trim()}" }
                feishuNotify('UNSTABLE', msg)
            }
        }

        aborted {
            script {
                feishuNotify('ABORTED', '⏹ **构建被手动取消**')
            }
        }
    }
}
