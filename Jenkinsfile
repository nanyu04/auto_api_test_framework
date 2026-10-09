pipeline {
    agent any

    parameters {
        choice(
            name: 'ENV',
            choices: ['dev', 'test', 'staging', 'prod'],
            description: '闂傚倷绶￠崑鍕囬幍顔瑰亾濮樸儱濡奸棁澶愭倵閿濆骸骞樻俊鍙夋倐閺岋絽顭ㄦ惔锛勪哗濡?
        )
        choice(
            name: 'TEST_LEVEL',
            choices: ['smoke', 'regression', 'all'],
            description: '闂傚倷绶￠崑鍕囬幍顔瑰亾濮樸儱濡奸棁澶愭倵閿濆骸骞樻俊鍙夋倐閺屻倝鎮℃惔鈩冩濠?
        )
        string(
            name: 'MARKER',
            defaultValue: '',
            description: '闂備胶鍘ч〃搴㈢濠婂牊鍋╅柣鎰靛墰閳?marker闂備焦瀵х粙鎴︽嚐椤栫偑鈧?P0 闂備胶鎳撻悺銊╂偋濠婂牆姹查柍褜鍓涚槐?
        )
        booleanParam(
            name: 'MOCK_MODE',
            defaultValue: false,
            description: '闂備礁鎲￠崙褰掑垂閹惰棄鏋?Mock 婵犵妲呴崹顏堝焵椤掆偓绾绢厾娑甸埀顒勬⒑閹稿海鈽夐柣妤€鎳愮划顓熷緞鐎ｎ剛鎳濆┑鐘绘涧閿曪箓銆呴銏╃唵闁煎摜鏁告晶鐢告煕鎼淬垺灏︾€殿噣娼ч濂稿川椤撗勫尃闂?
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

                // 闂佽崵濮村ú鈺咁敋瑜戦妵鎰板炊椤€虫贡閳ь剨缍嗛崢鎯ｉ崫銉х＝濞达綀顫夌亸浼存煟?                def total = 0
                def passed = 0
                def failed = 0
                def skipped = 0

                try {
                    def resultFile = findFiles(glob: "${env.REPORTS_DIR}/**/*-result.json")
                    echo "闂備胶鎳撻悘姘跺磿閹惰棄鏄?${resultFile.size()} 濠电偞鍨堕幖鈺傜濠靛牏鐭堥悗闈涙啞鐎氭岸鏌￠崶鈺佇ユ繛澶堝灲閺岋紕鈧綆鍋嗛惌瀣煛鐎ｎ亜鏆炵紒?
                } catch (err) {
                    echo "闂備礁鎼崯鐗堟叏閻㈠灚鍏滈柛鎾茬劍鐎氭岸鎮归崶銊ョ祷缂佸弶瀵х换娑㈠级閹搭厼鍓甸梺浼欏瘜閸ㄥ磭妲愰幒妤€绠婚悗鐢告櫜閸? ${err}"
                }
            }

            // 闂備礁鎲￠悷锕傚垂閸ф鐒垫い鎴ｆ硶缁愭梹銇勯妷顖滅ɑ缂佸锕弫鍐磼濡も偓娴滅偓鎱ㄥΟ澶稿惈闁告瑢鍋?
            script {
                def status = currentBuild.result ?: "SUCCESS"
                def statusIcon = status == "SUCCESS" ? "闂? : "闂?
                def duration = currentBuild.durationString ?: ""
                def testSummary = ""

                // 濠?allure 闂備胶顢婄紙浼村磿闁秴绠熼柨鐔哄У閸庡孩銇勯弮鍥т汗缂佸鐏濋埥澶愬箼閸愩劌绠洪悷婊堫暒缁舵艾鐣烽敐澶婂唨闁靛ě浣镐沪闂佽崵濮村ú锕€煤濠婂懎鍨濋柧蹇氼潐婵?                try {
                    def summaryFile = "${env.REPORTS_DIR}/export/statistics.json"
                    if (fileExists(summaryFile)) {
                        def summary = readJSON file: summaryFile
                        def total = summary.statistic.total ?: 0
                        def passed = summary.statistic.passed ?: 0
                        def failed = summary.statistic.failed ?: 0
                        def skipped = summary.statistic.skipped ?: 0
                        testSummary = "闂傚倷绶￠崑鍛┍閾忚宕? ${passed} | 濠电姰鍨洪崕鑲╁垝閸撗勫枂? ${failed} | 闂佽崵濮撮幖顐︽偪閸モ晜宕? ${skipped} | 闂備浇顕栭崜姘ｉ幒妤婃晣? ${total}"
                    }
                } catch (err) {
                    testSummary = "婵犵數鍋炲娆擃敄閸儲鍎婃い鏍仜缁犮儳鎲搁幋锔衡偓渚€骞嬮悩顐壕闁荤喓澧楀﹢浼存煕?
                }

                def message = """{
                    "msg_type": "interactive",
                    "card": {
                        "header": {
                            "title": {
                                "tag": "plain_text",
                                "content": "${statusIcon} API 闂備胶鍘ч〃搴㈢濠婂嫭鍙忛柍鍝勬噹缁€宀勬煛瀹ュ啫濡块柕鍫熸尦閹?${status}"
                            },
                            "template": "${status == "SUCCESS" ? "green" : "red"}"
                        },
                        "elements": [
                            {
                                "tag": "div",
                                "text": {
                                    "tag": "lark_md",
                                    "content": "**闂備胶绮划鐘诲垂娴兼番鈧?*: ${params.ENV}\\n**闂備浇鍋愰崢褔宕鈷?*: ${params.TEST_LEVEL}\\n**Mock**: ${params.MOCK_MODE}\\n${testSummary ? "**缂傚倸鍊烽悞锕傚箰婵犳碍鍊?*: ${testSummary}" : ""}\\n**闂備浇鍋愭晶妤呫€冮崱妤婃富?*: ${duration}"
                                }
                            },
                            {
                                "tag": "hr"
                            },
                            {
                                "tag": "div",
                                "text": {
                                    "tag": "lark_md",
                                    "content": "**濠电偛顕慨楣冾敋瑜庨幈?*: ${JOB_NAME}\\n**闂備礁鎼鍛偓姘煎墰缁?*: #${BUILD_NUMBER}"
                                }
                            },
                            {
                                "tag": "action",
                                "actions": [
                                    {
                                        "tag": "button",
                                        "text": {
                                            "tag": "plain_text",
                                            "content": "闂備礁鎼悮顐﹀磿閸愯鑰块柛娑欐綑缁狀噣鏌曟径鍫濆姕闁?
                                        },
                                        "type": "link",
                                        "url": "${BUILD_URL}allure"
                                    },
                                    {
                                        "tag": "button",
                                        "text": {
                                            "tag": "plain_text",
                                            "content": "闂備礁鎼悮顐﹀磿閸愯鑰块柛娑欐綑缁犲磭鎲稿澶婃槬婵°倕鎳庨惌?
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