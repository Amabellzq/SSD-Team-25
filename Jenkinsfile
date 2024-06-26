pipeline {
    agent any

    environment {
        GITHUB_PAT = credentials('GITHUB_PAT')
        GIT_BRANCH = 'main' // Set your desired branch here or make it a parameter
        GIT_REPO = credentials('GIT_REPO')
        REPO_DIR = "${WORKSPACE}/"
    }

      stages {
        stage('Clone or Update Repository') {
            steps {
                withCredentials([string(credentialsId: 'GITHUB_PAT', variable: 'GITHUB_PAT')]) {
                    // Use the GITHUB_PAT to configure credentials
                    sh 'git config --global credential.helper store'
                    sh 'echo "https://${GITHUB_PAT}:x-oauth-basic@github.com" > ~/.git-credentials'
                    // Check if the directory exists
                    script {
                        if (fileExists(REPO_DIR)) {
                            // If it exists, pull the latest changes
                            dir(REPO_DIR) {
                                sh 'git pull origin ${GIT_BRANCH}'
                            }
                        } else {
                            // If it doesn't exist, clone the repository
                            sh "git clone --branch ${GIT_BRANCH} ${GIT_REPO} ${REPO_DIR}"
                        }
                    }
                }
            }
        }

        stage('Load Credentials') {
            steps {
                withCredentials([
                    string(credentialsId: 'MYSQL_ROOT_PASSWORD', variable: 'MYSQL_ROOT_PASSWORD'),
                    string(credentialsId: 'MYSQL_DATABASE', variable: 'MYSQL_DATABASE'),
                    string(credentialsId: 'MYSQL_ADMIN_USER', variable: 'MYSQL_ADMIN_USER'),
                    string(credentialsId: 'MYSQL_ADMIN_PASSWORD', variable: 'MYSQL_ADMIN_PASSWORD'),
                    string(credentialsId: 'MYSQL_MERCHANT_USER', variable: 'MYSQL_MERCHANT_USER'),
                    string(credentialsId: 'MYSQL_MERCHANT_PASSWORD', variable: 'MYSQL_MERCHANT_PASSWORD'),
                    string(credentialsId: 'MYSQL_USER', variable: 'MYSQL_USER'),
                    string(credentialsId: 'MYSQL_USER_PASSWORD', variable: 'MYSQL_USER_PASSWORD'),
                    string(credentialsId: 'MYSQL_READONLY_USER', variable: 'MYSQL_READONLY_USER'),
                    string(credentialsId: 'MYSQL_READONLY_PASSWORD', variable: 'MYSQL_READONLY_PASSWORD'),
                    string(credentialsId: 'MYSQL_HOST', variable: 'MYSQL_HOST')
                ]) {
                    script {
                        // Create the .env file with the required environment variables
                        def envContent = ""
                        envContent += "MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}\n"
                        envContent += "MYSQL_DATABASE=${MYSQL_DATABASE}\n"
                        envContent += "MYSQL_ADMIN_USER=${MYSQL_ADMIN_USER}\n"
                        envContent += "MYSQL_ADMIN_PASSWORD=${MYSQL_ADMIN_PASSWORD}\n"
                        envContent += "MYSQL_MERCHANT_USER=${MYSQL_MERCHANT_USER}\n"
                        envContent += "MYSQL_MERCHANT_PASSWORD=${MYSQL_MERCHANT_PASSWORD}\n"
                        envContent += "MYSQL_USER=${MYSQL_USER}\n"
                        envContent += "MYSQL_USER_PASSWORD=${MYSQL_USER_PASSWORD}\n"
                        envContent += "MYSQL_READONLY_USER=${MYSQL_READONLY_USER}\n"
                        envContent += "MYSQL_READONLY_PASSWORD=${MYSQL_READONLY_PASSWORD}\n"
                        envContent += "MYSQL_HOST=${MYSQL_HOST}\n"

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
                 script {
                    def flake8Status = sh(script: 'pipx run flake8 . > flake8_report.txt', returnStatus: true)
                    if (flake8Status != 0) {
                        echo "flake8 found issues. Check the report at flake8_report.txt"
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
                    recordIssues tools: [flake8(pattern: "${REPO_DIR}flake8_report.txt")]

              sh 'rm -f .env'
        }

        cleanWs()
    }
    }
}
