pipeline {
    agent any

    parameters {
        choice(name: 'ENV', choices: ['dev','test','staging','prod'], description: 'test environment')
        choice(name: 'TEST_LEVEL', choices: ['smoke','regression','all'], description: 'test scope')
        string(name: 'MARKER', defaultValue: '', description: 'custom marker')
        booleanParam(name: 'MOCK_MODE', defaultValue: false, description: 'mock mode')
    }

    environment {
        REPORTS_DIR = "${WORKSPACE}/reports/allure"
        FEISHU_URL = 'https://open.feishu.cn/open-apis/bot/v2/hook/91e4d0a5-ed8c-4393-ab8a-2f1e8d631954'
    }

    stages {
        stage('Checkout') { steps { checkout scm } }
        stage('Setup') {
            steps {
                sh 'python3 -m venv .venv'
                sh '. .venv/bin/activate && pip install --upgrade pip -q'
                sh '. .venv/bin/activate && pip install -r requirements.txt -q'
            }
        }
        stage('Config') {
            steps {
                script {
                    def envFile = ".env.${params.ENV}"
                    if (fileExists(envFile)) {
                        sh "cp .env.${params.ENV} .env"
                    }
                }
            }
        }
        stage('Test') {
            steps {
                script {
                    def a = []
                    if (params.TEST_LEVEL == 'smoke') { a << '-m'; a << 'smoke' }
                    if (params.MARKER) { a << '-m'; a << params.MARKER }
                    if (params.MOCK_MODE) { a << '--mode=mock' }
                    sh ". .venv/bin/activate && pytest ${a.join(' ')} --alluredir ${env.REPORTS_DIR} tests/ --timeout=60 -n auto"
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

