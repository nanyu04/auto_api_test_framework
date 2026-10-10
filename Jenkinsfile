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
    // ==========================================================================
    // ⚠️⚠️ 千万别把工作区路径改成带中文的！否则所有 bat 步骤会静默卡死一小时 ⚠️⚠️
    //
    // 事故现象（2026-10-10 构建 #25~#30）：stage ② 的 bat 步骤一行输出都没有，
    //   一直挂到流水线 60 分钟超时；同一构建里的 powershell 步骤却是正常的。
    //
    // 真正原因（已在本机做 A/B 实验确认）：
    //   1. Jenkins（JDK 21）把 durable-task 的临时脚本 jenkins-wrap.bat 按 UTF-8 写盘；
    //   2. cmd.exe 执行 .bat 时按系统 ANSI 代码页(936/GBK)解析文件里的路径；
    //   3. 任务名是中文 → 默认工作区 C:\Users\29325\.jenkins\workspace\xzs后端项目api测试，
    //      .bat 里的中文路径被解成乱码 → cmd 找不到 jenkins-main.bat，
    //      也建不出 Jenkins 要轮询的 jenkins-log.txt；
    //   4. Jenkins 永远等不到日志文件 → 步骤既不报错也不结束 → 静默挂到超时。
    //   （powershell 步骤用 -EncodedCommand，编码无关，所以不受影响；
    //     Allure 插件走的是 Java 直接起进程，也不受影响。）
    // 实验对照：同一份 wrap 脚本，放 ASCII 路径下 → 正常产出 jenkins-log.txt；
    //           放中文路径下 → 什么都没有。隔壁 ASCII 任务 py-api-test-pipeline 的 bat 全部正常。
    //
    // 结论：工作区必须是纯 ASCII。这里用 customWorkspace 固定到 D 盘英文目录。
    // ==========================================================================
    agent {
        node {
            label 'built-in'                              // 固定在内置节点（build-agent-01 当前是离线的）
            customWorkspace 'D:/jenkins/ws/xzs-api-test'  // 纯 ASCII，不要再改回中文路径
        }
    }

    tools {
        jdk "jdk8"
    }

    options {
        timestamps()
        timeout(time: 60, unit: "MINUTES")
        buildDiscarder(logRotator(numToKeepStr: "20"))
        disableConcurrentBuilds()
        skipDefaultCheckout()     // ① 里已显式 checkout scm，跳过开头那次自动拉取
    }

    parameters {
        choice(name: 'ENV', choices: ['dev','test','staging','prod'], description: '选择测试环境')
        choice(name: 'TEST_LEVEL', choices: ['smoke','regression','all'], description: '测试范围')
        string(name: 'MARKER', defaultValue: '', description: '自定义 pytest marker（优先级高于测试范围，可用 and/or/not）')
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
        stage('① getcode') {
            steps { checkout scm }
        }

        stage('② envprepare') {
            steps {
                script {
                    // 单独给这一步加超时：万一再出现卡死，20 分钟就带明确报错结束，
                    // 而不是静默等满一小时的流水线超时。
                    timeout(time: 20, unit: 'MINUTES') {
                        // ① 检查 python 是否被 WindowsApps 占位符劫持
                        //    （被劫持时 python 会去弹微软商店，在无桌面会话里就会卡住）
                        def pyOut = bat(returnStdout: true, script: 'where python').trim()
                        def pythonPath = pyOut ? pyOut.readLines().first() : ''
                        echo "🔍 使用的 Python: ${pythonPath}"
                        if (!pythonPath || pythonPath.toLowerCase().contains('windowsapps')) {
                            error "Python 不可用或被 WindowsApps 占位符劫持（where python 首个结果: '${pythonPath}'），请把真实 Python 的路径放到 PATH 最前面"
                        }

                        echo "🔄 创建虚拟环境 (${env.VENV_DIR}) ..."
                        bat """
                            if exist "${env.VENV_DIR}" rmdir /s /q "${env.VENV_DIR}" || exit /b 1
                            python -m venv "${env.VENV_DIR}" || exit /b 1
                        """

                        echo "📦 安装依赖（pip 缓存目录: ${env.PIP_CACHE_DIR}）..."
                        // 直接用 venv 里的 python，不依赖 activate.bat；
                        // 每条命令都用 || exit /b 1 提前失败，避免装挂了还报成功。
                        bat """
                            if not exist "${env.PIP_CACHE_DIR}" mkdir "${env.PIP_CACHE_DIR}" || exit /b 1
                            "${env.VENV_DIR}\\Scripts\\python.exe" -m pip install --upgrade pip --progress-bar off -i https://pypi.tuna.tsinghua.edu.cn/simple || exit /b 1
                            "${env.VENV_DIR}\\Scripts\\python.exe" -m pip install -r requirements.txt --progress-bar off --cache-dir "${env.PIP_CACHE_DIR}" -i https://pypi.tuna.tsinghua.edu.cn/simple || exit /b 1
                            "${env.VENV_DIR}\\Scripts\\python.exe" -m pytest --version || exit /b 1
                        """

                        echo "✅ 环境准备完成"
                    }
                }
            }
        }

        stage('③ config') {
            steps {
                script {
                    def envFile = ".env.${params.ENV}"
                    if (fileExists(envFile)) {
                        bat "copy /Y \"${envFile}\" .env"
                        echo "✅ 已加载配置: ${envFile}"
                    } else {
                        // 注意：.env / .env.* 都在 .gitignore 里，CI 拉下来的工作区没有这些文件，
                        // 此时 config 会退回到内置默认值（BASE_URL=http://127.0.0.1:8000）。
                        echo "⚠ 未找到 ${envFile}，跳过（将使用 config/__init__.py 里的默认配置）"
                    }
                }
            }
        }

        stage('④ test') {
            steps {
                script {
                    // 先清理上次的报告（junit 和 allure 一起清，避免残留旧报告）
                    bat "if exist reports rmdir /S /Q reports"

                    // marker 优先级：手填 MARKER > TEST_LEVEL（all = 不加过滤条件）
                    def marker = params.MARKER?.trim() ?: (params.TEST_LEVEL == 'all' ? '' : params.TEST_LEVEL)
                    def args = []
                    if (marker) {
                        args << '-m' << "\"${marker}\""   // 加引号，支持 "smoke and not slow" 这种写法
                    }
                    if (params.MOCK_MODE) {
                        args << '--mode=mock'
                    }
                    args << '--alluredir' << env.REPORTS_DIR
                    args << '-v'
                    args << '--junitxml=reports/junit.xml'
                    args << '--timeout=60'
                    args << 'tests/'

                    echo "⏳ 执行: pytest ${args.join(' ')}"

                    timeout(time: 30, unit: 'MINUTES') {
                        try {
                            bat "\"${env.VENV_DIR}\\Scripts\\python.exe\" -m pytest ${args.join(' ')}"
                        } catch (Exception e) {
                            // 用例失败不影响后面出报告（构建状态由 junit 的失败用例数决定）
                            echo "⚠ pytest 返回了非零退出码（有失败用例），继续收集报告..."
                        }
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