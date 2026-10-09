// ============================================================
//  飞书通知函数
// ============================================================
def feishuNotify(status, summary) {
    def colorMap = [
        'SUCCESS': 'green', 'FAILURE': 'red',
        'UNSTABLE': 'yellow', 'ABORTED': 'grey',
    ]
    def titleMap = [
        'SUCCESS': '✅ 构建成功', 'FAILURE': '❌ 构建失败',
        'UNSTABLE': '⚠️ 构建不稳定', 'ABORTED': '⏹ 构建已取消',
    ]
    def color = colorMap.get(status, 'red')
    def title = titleMap.get(status, '构建通知')

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
            { "tag": "div", "fields": [
                { "is_short": true, "text": { "tag": "lark_md", "content": "**🆔 构建编号**\\n${env.BUILD_NUMBER}" } },
                { "is_short": true, "text": { "tag": "lark_md", "content": "**🌿 分支**\\n${branchName}" } },
                { "is_short": true, "text": { "tag": "lark_md", "content": "**🔧 环境**\\n${params.ENV}" } },
                { "is_short": true, "text": { "tag": "lark_md", "content": "**📊 测试范围**\\n${params.TEST_LEVEL}" } }
            ]},
            { "tag": "hr" },
            { "tag": "div", "fields": [
                { "is_short": true, "text": { "tag": "lark_md", "content": "**📅 时间**\\n${buildTime}" } },
                { "is_short": true, "text": { "tag": "lark_md", "content": "**⏱ 耗时**\\n${duration}" } }
            ]},
            { "tag": "hr" },
            { "tag": "div", "text": { "tag": "lark_md", "content": "${summary}" } },
            { "tag": "hr" },
            { "tag": "action", "actions": [
                { "tag": "button", "text": { "tag": "plain_text", "content": "🔗 查看构建" }, "type": "primary",
                  "multi_url": { "url": "${env.BUILD_URL}", "android_url": "", "ios_url": "", "pc_url": "" } },
                { "tag": "button", "text": { "tag": "plain_text", "content": "📊 Allure 报告" }, "type": "default",
                  "multi_url": { "url": "${env.BUILD_URL}allure", "android_url": "", "ios_url": "", "pc_url": "" } }
            ]}
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

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        disableConcurrentBuilds()
    }

    parameters {
        choice(name: 'ENV', choices: ['dev','test','staging','prod'], description: '选择测试环境')
        choice(name: 'TEST_LEVEL', choices: ['smoke','regression','all'], description: '测试范围')
        string(name: 'MARKER', defaultValue: '', description: '自定义 pytest marker')
        booleanParam(name: 'MOCK_MODE', defaultValue: false, description: '启用 Mock 模式')
    }

    environment {
        PYTHONIOENCODING = 'utf-8'
        PYTHONUNBUFFERED = '1'
        PIP_INDEX_URL    = 'https://pypi.tuna.tsinghua.edu.cn/simple'
        PIP_TRUSTED_HOST = 'pypi.tuna.tsinghua.edu.cn'
        PIP_DISABLE_PIP_VERSION_CHECK = '1'

        FEISHU_URL   = 'https://open.feishu.cn/open-apis/bot/v2/hook/91e4d0a5-ed8c-4393-ab8a-2f1e8d631954'
        PROJECT_NAME = 'API 接口自动化测试'
    }

    stages {
        stage('① 环境准备') {
            steps {
                bat '''
                    if exist .venv rmdir /s /q .venv
                    python -m venv .venv
                    .venv\\Scripts\\python.exe -m pip install -r requirements.txt
                '''
            }
        }

        stage('② 加载配置') {
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

        stage('③ 执行测试') {
            steps {
                bat '''
                    if exist reports rmdir /s /q reports
                    mkdir reports
                    .venv\\Scripts\\python.exe -m pytest -v --junitxml=reports/junit.xml
                '''
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'reports/junit.xml'
            script {
                try {
                    allure results: [[path: 'allure-results']]
                } catch (Exception e) {
                    echo "⚠ Allure 报告发布失败: ${e.message}"
                }
            }
            bat '''
                if exist .venv rmdir /s /q .venv
                if exist .pytest_cache rmdir /s /q .pytest_cache
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