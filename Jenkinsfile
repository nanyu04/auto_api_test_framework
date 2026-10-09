// ==========================================
// 1. 自定义方法必须放在 pipeline 块的外面！
// ==========================================
def feishuNotify(status, summary) {
    def color = (status == 'SUCCESS') ? 'green' : 'red'
    def title = (status == 'SUCCESS') ? '✅ 构建成功' : '❌ 构建失败'

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
                    { "is_short": true, "text": { "tag": "lark_md", "content": "**🌿 分支**\\n${env.BRANCH_NAME}" } },
                    { "is_short": true, "text": { "tag": "lark_md", "content": "**🔧 环境**\\n${params.ENV}" } },
                    { "is_short": true, "text": { "tag": "lark_md", "content": "**📊 测试范围**\\n${params.TEST_LEVEL}" } }
                ]
            },
            { "tag": "hr" },
            {
                "tag": "div",
                "fields": [
                    { "is_short": true, "text": { "tag": "lark_md", "content": "**📅 时间**\\n${currentBuild.timeInMillis ? new Date(currentBuild.timeInMillis).format('yyyy-MM-dd HH:mm:ss') : 'N/A'}" } },
                    { "is_short": true, "text": { "tag": "lark_md", "content": "**⏱ 耗时**\\n${currentBuild.durationString?.replace(' and counting', '') ?: 'N/A'}" } }
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

    // 修复了单引号不解析变量的问题，改用三引号包裹
    powershell """
        try {
            $$body = '''${cardJson}'''
            $$response = Invoke-RestMethod -Uri ${env.FEISHU_URL} -Method Post -ContentType "application/json" -Body $$body
            if ($$response.code -ne 0) {
                Write-Warning "飞书通知返回异常: $$($$response | ConvertTo-Json -Compress)"
            } else {
                Write-Host "飞书通知发送成功 (status=${status})"
            }
        } catch {
            Write-Warning "飞书通知发送失败: $$($$_ | Out-String)"
        }
    """
}

// ==========================================
// 2. pipeline 块开始
// ==========================================
pipeline {
    agent any

    parameters {
        choice(name: 'ENV', choices: ['dev','test','staging','prod'], description: '选择测试环境')
        choice(name: 'TEST_LEVEL', choices: ['smoke','regression','all'], description: '测试范围')
        string(name: 'MARKER', defaultValue: '', description: '自定义 pytest marker')
        booleanParam(name: 'MOCK_MODE', defaultValue: false, description: '启用 Mock 模式')
    }

    environment {
        REPORTS_DIR   = 'reports/allure'
        FEISHU_URL    = 'https://open.feishu.cn/open-apis/bot/v2/hook/91e4d0a5-ed8c-4393-ab8a-2f1e8d631954'
        // 注意这里改成了正斜杠 /，防止 Groovy 解析转义字符报错
        PIP_CACHE_DIR = "${WORKSPACE}/pip_cache"
        PROJECT_NAME  = 'API 接口自动化测试'
    }

    stages {
        stage('① 拉取代码') {
            steps { checkout scm }
        }

        stage('② 环境准备') {
            steps {
                bat 'if not exist .venv python -m venv .venv'
                bat 'call .venv\\Scripts\\activate.bat && pip install --upgrade pip -q'
                bat "call .venv\\Scripts\\activate.bat && pip install -r requirements.txt -q --cache-dir ${PIP_CACHE_DIR}"
            }
        }

        stage('③ 加载配置') {
            steps {
                script {
                    def envFile = ".env." + params.ENV
                    if (fileExists(envFile)) {
                        bat "copy /Y ${envFile} .env"
                    } else {
                        echo "⚠ 未找到 ${envFile}，跳过"
                    }
                }
            }
        }

        stage('④ 执行测试') {
            steps {
                script {
                    def args = []
                    if (params.TEST_LEVEL == 'smoke')     { args.add('-m'); args.add('smoke') }
                    if (params.MARKER?.trim())            { args.add('-m'); args.add(params.MARKER.trim()) }
                    if (params.MOCK_MODE)                 { args.add('--mode=mock') }
                    args << '--alluredir' << env.REPORTS_DIR
                    args << 'tests/' << '--timeout=60'
                    bat "call .venv\\Scripts\\activate.bat && pytest ${args.join(' ')}"
                }
            }
        }
    }

    post {
        always {
            allure results: [[path: env.REPORTS_DIR]]
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