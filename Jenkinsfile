pipeline {
    agent any

    parameters {
        choice(
            name: 'ENV',
            choices: ['dev', 'test', 'staging', 'prod'],
            description: '闂傚倸鍊风欢锟犲磻閸曨垁鍥箥椤旂懓浜炬慨妯稿劚婵″ジ妫佹径鎰€甸柨婵嗛楠炴ɑ淇婇崣澶嬪€愰柡宀嬬到椤劍鎯旈敍鍕摋婵?
        )
        choice(
            name: 'TEST_LEVEL',
            choices: ['smoke', 'regression', 'all'],
            description: '闂傚倸鍊风欢锟犲磻閸曨垁鍥箥椤旂懓浜炬慨妯稿劚婵″ジ妫佹径鎰€甸柨婵嗛楠炴ɑ淇婇崣澶嬪€愰柡灞诲€濋幃鈩冩償閳╁啯顔勬繝?
        )
        string(
            name: 'MARKER',
            defaultValue: '',
            description: '闂傚倷鑳堕崢褔銆冩惔銏㈩洸婵犲﹤鐗婇崑鈺呮煟閹伴潧澧伴柍?marker闂傚倷鐒︾€笛呯矙閹达附鍤愭い鏍亼閳?P0 闂傚倷鑳堕幊鎾绘偤閵娾晜鍋嬫繝濠傜墕濮规煡鏌嶈閸撴稓妲?
        )
        booleanParam(
            name: 'MOCK_MODE',
            defaultValue: false,
            description: '闂傚倷绀侀幉锟犲礄瑜版帒鍨傞柟鎯版閺?Mock 濠电姷顣藉Σ鍛村垂椤忓牆鐒垫い鎺嗗亾缁剧虎鍘惧☉鐢稿焵椤掑嫭鈷戦柟绋挎捣閳藉鏌ｅΔ鈧幊鎰垝椤撶喎绶為悗锝庡墰閹虫繂鈹戦悩缁樻锭闁挎洩绠撻妴鍛搭敃閵忊晝鍞甸梺鐓庢憸閺佸憡鏅堕悽鍛婄厱閹兼番鍨虹亸锔锯偓娈垮櫍濞佳囶敇婵傜宸濇い鎾楀嫬灏冮梻?
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

                // 闂備浇宕垫慨鏉懨洪埡鍜佹晪鐟滄垿濡甸幇鏉跨倞妞ゎ兘鈧櫕璐￠柍褜鍓ㄧ紞鍡涘储閹灛锝夊传閵壯咃紳婵炶揪缍€椤浜告导瀛樼厽?                def total = 0
                def passed = 0
                def failed = 0
                def skipped = 0

                try {
                    def resultFile = findFiles(glob: "${env.REPORTS_DIR}/**/*-result.json")
                    echo "闂傚倷鑳堕幊鎾绘倶濮樿泛纾块柟鎯版閺?${resultFile.size()} 婵犵數鍋為崹鍫曞箹閳哄倻顩叉繝闈涚墢閻牓鎮楅棃娑欏暈閻庢碍宀搁弻锟犲炊閳轰絿銉︾箾婢跺牆鐏查柡宀嬬磿閳ь剨缍嗛崑鍡涙儗鐎ｎ喗鐓涢悗锝庝簻閺嗙偟绱?
                } catch (err) {
                    echo "闂傚倷绀侀幖顐﹀疮閻楀牊鍙忛柣銏犵仛閸忔粓鏌涢幘鑼妽閻庢碍宀搁幃褰掑炊閵娿儳绁风紓浣稿级鐎笛呮崲濞戙垹绾ч柟鎼幖閸撶敻姊烘导娆忕槣闁搞劌纾Σ鎰板箳濡も偓缁犲鎮楅悽鍛婃珳闁? ${err}"
                }
            }

            // 闂傚倷绀侀幉锟犳偡閿曞倸鍨傞柛褎顨呴悞鍨亜閹达絾纭剁紒鎰⒐閵囧嫰濡烽婊吷戠紓浣割儏閿曨亪寮崘顔肩＜婵°倐鍋撳ù婊呭亾閹便劌螣婢剁鎯堥梺鍛婄憿閸?
            script {
                def status = currentBuild.result ?: "SUCCESS"
                def statusIcon = status == "SUCCESS" ? "闂? : "闂?
                def duration = currentBuild.durationString ?: ""
                def testSummary = ""

                // 婵?allure 闂傚倷鑳堕、濠勭礄娴兼潙纾块梺顒€绉寸粻鐔兼煥閻斿搫校闁稿骸瀛╅妵鍕籍閸パ傛睏缂備礁顦悘婵嬪煡婢舵劕绠奸柛鎰╁妼缁犳椽鎮峰鍫殥缂佽埖鑹鹃悾鐑芥晲婢跺﹤鍞ㄩ梺闈浤涙担闀愭勃闂備浇宕垫慨鏉懨洪敃鈧叅婵犲﹤鎳庨崹婵嬫煣韫囨凹娼愬┑?                try {
                    def summaryFile = "${env.REPORTS_DIR}/export/statistics.json"
                    if (fileExists(summaryFile)) {
                        def summary = readJSON file: summaryFile
                        def total = summary.statistic.total ?: 0
                        def passed = summary.statistic.passed ?: 0
                        def failed = summary.statistic.failed ?: 0
                        def skipped = summary.statistic.skipped ?: 0
                        testSummary = "闂傚倸鍊风欢锟犲磻閸涱喚鈹嶉柧蹇氼潐瀹? ${passed} | 婵犵數濮伴崹娲磿閼测晛鍨濋柛鎾楀嫬鏋? ${failed} | 闂備浇宕垫慨鎾箹椤愶附鍋柛銉㈡櫆瀹? ${skipped} | 闂傚倷娴囬鏍礈濮橆儵锝夊箳濡ゅ﹥鏅? ${total}"
                    }
                } catch (err) {
                    testSummary = "濠电姷鏁搁崑鐐差焽濞嗘搩鏁勯柛顐犲劜閸庡﹥銇勯弽顐粶缂佺姰鍎抽幉鎼佸箣閿旇　鍋撴笟鈧獮瀣偐椤愵澀澹曢梺鑽ゅ枔婢ф锕㈡导瀛樼厱?
                }

                def message = """{
                    "msg_type": "interactive",
                    "card": {
                        "header": {
                            "title": {
                                "tag": "plain_text",
                                "content": "${statusIcon} API 闂傚倷鑳堕崢褔銆冩惔銏㈩洸婵犲﹤瀚崣蹇涙煃閸濆嫭鍣圭紒鈧畝鍕厸鐎广儱鍟俊鍧楁煏閸喐灏﹂柟?${status}"
                            },
                            "template": "${status == "SUCCESS" ? "green" : "red"}"
                        },
                        "elements": [
                            {
                                "tag": "div",
                                "text": {
                                    "tag": "lark_md",
                                    "content": "**闂傚倷鑳剁划顖滃垝閻樿鍨傚ù鍏肩暘閳?*: ${params.ENV}\\n**闂傚倷娴囬崑鎰板储瑜斿畷顖烆敃閳?*: ${params.TEST_LEVEL}\\n**Mock**: ${params.MOCK_MODE}\\n${testSummary ? "**缂傚倸鍊搁崐鐑芥倿閿曞倸绠板┑鐘崇閸?*: ${testSummary}" : ""}\\n**闂傚倷娴囬崑鎰櫠濡ゅ懌鈧啴宕卞Δ濠冨瘜?*: ${duration}"
                                }
                            },
                            {
                                "tag": "hr"
                            },
                            {
                                "tag": "div",
                                "text": {
                                    "tag": "lark_md",
                                    "content": "**婵犵數鍋涢顓熸叏妤ｅ喚鏁嬬憸搴ㄥ箞?*: ${JOB_NAME}\\n**闂傚倷绀侀幖顐︻敄閸涱垪鍋撳鐓庡缂?*: #${BUILD_NUMBER}"
                                }
                            },
                            {
                                "tag": "action",
                                "actions": [
                                    {
                                        "tag": "button",
                                        "text": {
                                            "tag": "plain_text",
                                            "content": "闂傚倷绀侀幖顐ゆ偖椤愶箑纾块柛鎰嚋閼板潡鏌涘☉娆愮稇缂佺媭鍣ｉ弻鏇熷緞閸繂濮曢梺?
                                        },
                                        "type": "link",
                                        "url": "${BUILD_URL}allure"
                                    },
                                    {
                                        "tag": "button",
                                        "text": {
                                            "tag": "plain_text",
                                            "content": "闂傚倷绀侀幖顐ゆ偖椤愶箑纾块柛鎰嚋閼板潡鏌涘☉娆愮稇缂佺姴纾幉绋款吋婢跺﹥妲┑掳鍊曢幊搴ㄦ儗?
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