pipeline {
    agent any
    environment {
        GITHUB_PAT = credentials('GITHUB_PAT')
        GIT_BRANCH = 'main' // Set your desired branch here or make it a parameter
        GIT_REPO = credentials('GIT_REPO')
        REPO_DIR = "${WORKSPACE}/"
        FLASK_CONTAINER = 'flask'
    }
      stages {
       stage('Checkout') {
            steps {
                git url: "${GIT_REPO}", branch: "${GIT_BRANCH}", credentialsId: 'GITHUB_ACC'
            }
        }
        stage('Load Credentials') {
            steps {
                withCredentials([
                    string(credentialsId: 'MYSQL_ROOT_PASSWORD', variable: 'MYSQL_ROOT_PASSWORD'),
                    string(credentialsId: 'MYSQL_DATABASE', variable: 'MYSQL_DATABASE'),
                    string(credentialsId: 'MYSQL_ADMIN_USER', variable: 'MYSQL_ADMIN_USER'),
                    string(credentialsId: 'MYSQL_ADMIN_PASSWORD', variable: 'MYSQL_ADMIN_PASSWORD'),
                    string(credentialsId: 'MYSQL_HOST', variable: 'MYSQL_HOST'),
                    string(credentialsId: 'OUTLOOK_EMAIL', variable: 'OUTLOOK_EMAIL'),
                    string(credentialsId: 'OUTLOOK_PASSWORD', variable: 'OUTLOOK_PASSWORD'),
                    string(credentialsId: 'RECAPTCHA_PUBLIC_KEY', variable: 'RECAPTCHA_PUBLIC_KEY'),
                    string(credentialsId: 'RECAPTCHA_PRIVATE_KEY', variable: 'RECAPTCHA_PRIVATE_KEY'),
                    string(credentialsId: 'ENCRYPTION_KEY', variable: 'ENCRYPTION_KEY')

                ]) {
                    script {
                        // Create the .env file with the required environment variables
                        def envContent = ""
                        envContent += "MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}\n"
                        envContent += "MYSQL_DATABASE=${MYSQL_DATABASE}\n"
                        envContent += "MYSQL_ADMIN_USER=${MYSQL_ADMIN_USER}\n"
                        envContent += "MYSQL_ADMIN_PASSWORD=${MYSQL_ADMIN_PASSWORD}\n"
                        envContent += "MYSQL_HOST=${MYSQL_HOST}\n"
                        envContent += "OUTLOOK_EMAIL=${OUTLOOK_EMAIL}\n"
                        envContent += "OUTLOOK_PASSWORD=${OUTLOOK_PASSWORD}\n"
                        envContent += "RECAPTCHA_PUBLIC_KEY=${RECAPTCHA_PUBLIC_KEY}\n"
                        envContent += "RECAPTCHA_PRIVATE_KEY=${RECAPTCHA_PRIVATE_KEY}\n"
                        envContent += "ENCRYPTION_KEY=${ENCRYPTION_KEY}\n"

                        writeFile file: '.env', text: envContent
                    }
                }
            }
        }
        stage('OWASP Dependency-Check Vulnerabilities') {
            steps {
                dependencyCheck additionalArguments: '''
                    -o './'
                    -s './'
                    -f 'ALL'
                    --prettyPrint''', odcInstallation: 'OWASP Dependency-Check Vulnerabilities'

        dependencyCheckPublisher pattern: 'dependency-check-report.xml'
            }
        }
        stage('Code Analysis with Flake8') {
            steps {
                dir(REPO_DIR) {
                   sh(script: 'pipx run flake8 . > flake8_report.txt', returnStatus: true)
                }
            }
        }
        stage('Code Analysis with pylint') {
            steps {
                dir(REPO_DIR) {
                    script {
                        // Run pylint using pipx and capture the exit status
                        def pylintStatus = sh(script: 'pipx run pylint -f parseable --reports=no *.py > pylint_report.log', returnStatus: true)
                        if (pylintStatus != 0) {
                            echo "pylint found issues. Check the report at pylint_report.log"
                        } else {
                            echo "pylint completed successfully with no issues."
                        }
                    }
                }
            }
        }
        stage('Code Analysis with bandit') {
            steps {
                dir(REPO_DIR) {
                    script {
                        // Run bandit and capture the exit status
                        def banditStatus = sh(script: 'pipx run bandit -r . -f json -o bandit_report.json', returnStatus: true)
                        if (banditStatus != 0) {
                            echo "bandit found issues. Check the report at bandit_report.json"
                        } else {
                            echo "bandit completed successfully with no issues."
                        }
                    }
                }
            }
        }
        stage('Code Quality Check via SonarQube') {
            steps {
                script {
                    def scannerHome = tool 'SonarQube'
                    withSonarQubeEnv('SonarQube') {
                        sh """
                        ${scannerHome}/bin/sonar-scanner \
                        -Dsonar.projectKey=SSD_Grp25_OWASP \
                        -Dsonar.sources=. \
                        -Dsonar.python.coverage.reportPaths=${WORKSPACE}/SSD_Pipeline/coverage.xml \
                        -Dsonar.junit.reportPaths=${WORKSPACE}/SSD_Pipeline/report.xml
                        """
                    }
                }
    	    }
        }
        stage('Prepare SSL Certificates') {
            steps {
                withCredentials([
                    file(credentialsId: 'CRT_CERT', variable: 'CRT_FILE'),
                    file(credentialsId: 'SSL_KEY', variable: 'KEY_FILE')
                ]) {
                    script {
                        dir(REPO_DIR) {
                            // Ensure the nginx directory exists
                            sh 'mkdir -p nginx'

                            // Copy the secret files to the nginx directory
                            sh "cp ${CRT_FILE} nginx/fullchain.crt"
                            sh "cp ${KEY_FILE} nginx/shoppp.me.key"

                            // Ensure proper file permissions
                            sh 'chmod 600 nginx/fullchain.crt nginx/shoppp.me.key'
                        }
                    }
                }
            }
        }
        stage('Pytest') {
            steps {
                dir(REPO_DIR) {
                    script {
                        // Create virtual environment and install dependencies
                        sh """
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                        """

                        // Run pytest and generate a JUnit XML report
                        sh """
                        . venv/bin/activate
                        pytest -v --tb=long --junitxml=report.xml
                        """
                    }
                }
            }
        }
        stage('Build and Deploy') {
            steps {
                // Ensure a clean deployment by bringing down any existing containers
                sh 'docker-compose down --remove-orphans'
                // Use Docker Compose to build and start the services, using the .env file for configuration
                sh 'docker-compose up --build -d'
            }
        }
    }

post {
    always {
        script {

                    // Record Flake8 issues
                    recordIssues tools: [flake8(pattern: "flake8_report.txt")]
                    recordIssues (
                    enabledForFailure: true,
                    aggregatingResults: true,
                    tools: [pyLint(name: 'Pylint', pattern: 'pylint_report.log')]
                    )
                     //recordIssues tools: [bandit(pattern: 'bandit_report.json')]
                     //recordIssues enabledForFailure: true, tool: sonarQube()


              sh 'rm -f .env'
               cleanWs()
        }
    }
      success {
            echo 'All stages completed successfully.'
        }
        failure {
            echo 'One or more stages failed.'
        }

    }

}
