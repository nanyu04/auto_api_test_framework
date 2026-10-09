pipeline {
    agent any

    parameters {
        choice(
            name: 'ENV',
            choices: ['dev', 'test', 'staging', 'prod'],
            description: '闂備緡鍋勯ˇ鎵偓姘ュ妼闇夐悗锝庡幘濡叉悂鏌ｅ搴＄仩妞?
        )
        choice(
            name: 'TEST_LEVEL',
            choices: ['smoke', 'regression', 'all'],
            description: '闂備緡鍋勯ˇ鎵偓姘ュ妼闇夐悗锝庡幘濡叉悂鏌ら悡搴℃殭婵?
        )
        string(
            name: 'MARKER',
            defaultValue: '',
            description: '闂佺厧顨庢禍婊堟偩閻愵剛鈻?marker闂佹寧绋戦懟顖炪€?P0 闂佺懓鐡ㄩ悧婊堝汲閳ь剛绱?
        )
        booleanParam(
            name: 'MOCK_MODE',
            defaultValue: false,
            description: '闂佸憡鍑归崹鎶藉极?Mock 濠碘槅鍨埀顒€纾涵鈧梺鎸庣☉閻楀懐绮径瀣懝婵犻潧锕﹂々顐㈩熆閼哥數澧甸柛搴㈡尦瀵潧顓奸崨顓ф匠闂?
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
                    args << "--alluredir" << env.REPORTS_DIR
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
                       results: [[path: env.REPORTS_DIR]]

                // 闁荤姴娲╅褑銇愰崶顬″湱鈧綆鍘惧Σ鍝ョ磽娴ｈ灏伴柣?                def total = 0
                def passed = 0
                def failed = 0
                def skipped = 0

                try {
                    def resultFile = findFiles(glob: "${env.REPORTS_DIR}/**/*-result.json")
                    echo "闂佺懓鐏氶崕鎶藉春?${resultFile.size()} 婵炴垶鎼╂禍婵堢矈鐎靛憡瀚氶柡鍥╁Х濞夈垽鏌＄€ｎ偆鐭嬮柡瀣暞缁?
                } catch (err) {
                    echo "闂佸搫鍟版慨鐢垫兜閸撲焦瀚氶悹鍥ㄥ絻缁叉寧绻涢弶鎴創闁伙富鍨崇槐鎺楀箻鐎甸晲鍑? ${err}"
                }
            }

            // 闂佸憡鐟﹂崹鍧楀焵椤戣法绐旀い銉稻缁嬪﹪鏁冮崒妤€浜炬慨妯夸含閸欌偓
            script {
                def status = currentBuild.result ?: "SUCCESS"
                def statusIcon = status == "SUCCESS" ? "闂? : "闂?
                def duration = currentBuild.durationString ?: ""
                def testSummary = ""

                // 婵?allure 闂佺缈伴崕閬嶅箟閿熺姵鍎庢い鏃囧亹缁夊灝鈽夐幙鍐ㄥ箺鐟滈绶氬畷锝夊冀閵娧佸仦闁荤姴娲﹀ú婊呭垝閾忚濯?                try {
                    def summaryFile = "${env.REPORTS_DIR}/export/statistics.json"
                    if (fileExists(summaryFile)) {
                        def summary = readJSON file: summaryFile
                        def total = summary.statistic.total ?: 0
                        def passed = summary.statistic.passed ?: 0
                        def failed = summary.statistic.failed ?: 0
                        def skipped = summary.statistic.skipped ?: 0
                        testSummary = "闂備緡鍋呮穱铏规崲? ${passed} | 婵犮垺鍎肩划鍓ф喆? ${failed} | 闁荤姴鎼悿鍥╂崲? ${skipped} | 闂佽鍓氬Σ鎺楊敇? ${total}"
                    }
                } catch (err) {
                    testSummary = "濠电偞娼欓鍫ユ儊椤栫偛绠ョ憸鎴︺€侀幋鐘亾閻熺増婀伴柛?
                }

                def message = """{
                    "msg_type": "interactive",
                    "card": {
                        "header": {
                            "title": {
                                "tag": "plain_text",
                                "content": "${statusIcon} API 闂佺厧顨庢禍婊勬叏閳哄懎绀岄柡宥冨妿閵堟挳鎮?${status}"
                            },
                            "template": "${status == "SUCCESS" ? "green" : "red"}"
                        },
                        "elements": [
                            {
                                "tag": "div",
                                "text": {
                                    "tag": "lark_md",
                                    "content": "**闂佺粯绮犻崹浼淬€?*: ${params.ENV}\\n**闂佽偐鍘ч崯顐⒚?*: ${params.TEST_LEVEL}\\n**Mock**: ${params.MOCK_MODE}\\n${testSummary ? "**缂傚倷鐒﹂幐濠氭倶?*: ${testSummary}" : ""}\\n**闂佽偐澧楅〃鍡楊渻?*: ${duration}"
                                }
                            },
                            {
                                "tag": "hr"
                            },
                            {
                                "tag": "div",
                                "text": {
                                    "tag": "lark_md",
                                    "content": "**婵炲濮鹃褎鎱?*: ${JOB_NAME}\\n**闂佸搫顑呯€氼剛绱?*: #${BUILD_NUMBER}"
                                }
                            },
                            {
                                "tag": "action",
                                "actions": [
                                    {
                                        "tag": "button",
                                        "text": {
                                            "tag": "plain_text",
                                            "content": "闂佸搫琚崕鍐诧耿閸涙潙绠柕澶堝劜閸?
                                        },
                                        "type": "link",
                                        "url": "${BUILD_URL}allure"
                                    },
                                    {
                                        "tag": "button",
                                        "text": {
                                            "tag": "plain_text",
                                            "content": "闂佸搫琚崕鍐诧耿閸涙潙绠崇憸宥夊春濡ゅ懎鐭?
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