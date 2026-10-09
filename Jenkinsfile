pipeline {
    agent any
    parameters {
        choice(name: 'ENV', choices: ['dev','test','staging','prod'], description: 'test environment')
        choice(name: 'TEST_LEVEL', choices: ['smoke','regression','all'], description: 'test scope')
        string(name: 'MARKER', defaultValue: '', description: 'custom marker')
        booleanParam(name: 'MOCK_MODE', defaultValue: false, description: 'mock mode')
    }
    environment {
        REPORTS_DIR = 'reports/allure'
        FEISHU_URL = 'https://open.feishu.cn/open-apis/bot/v2/hook/91e4d0a5-ed8c-4393-ab8a-2f1e8d631954'
    }
    stages {
        stage('Checkout') { steps { checkout scm } }
        stage('Setup') {
            steps {
                bat 'python -m venv .venv'
                bat '.venv\Scripts\pip install --upgrade pip -q'
                bat '.venv\Scripts\pip install -r requirements.txt -q'
            }
        }
        stage('Config') {
            steps {
                script {
                    if (fileExists(".env." + params.ENV)) {
                        bat "copy /Y .env." + params.ENV + " .env"
                    }
                }
            }
        }
        stage('Test') {
            steps {
                script {
                    def a = []
                    if (params.TEST_LEVEL == 'smoke') { a.add('-m'); a.add('smoke') }
                    if (params.MARKER) { a.add('-m'); a.add(params.MARKER) }
                    if (params.MOCK_MODE) { a.add('--mode=mock') }
                    a.add('--alluredir'); a.add(env.REPORTS_DIR)
                    bat ".venv\\Scripts\\pytest " + a.join(" ") + " tests/ --timeout=60"
                }
            }
        }
    }
    post {
        always {
            allure results: [[path: env.REPORTS_DIR]]
        }
    }
}
