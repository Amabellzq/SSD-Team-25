pipeline {
    agent any

    environment {
        GITHUB_PAT = credentials('GITHUB_PAT')
        GIT_BRANCH = 'development-junwei' // Set your desired branch here or make it a parameter
        GIT_REPO = credentials('GIT_REPO')
    }

    stages {
        stage('Clone Repository') {
            steps {
                withCredentials([string(credentialsId: 'GITHUB_PAT', variable: 'GITHUB_PAT')]) {
                    // Use the GITHUB_PAT to clone the repository
                    sh 'git config --global credential.helper store'
                    sh 'echo "https://${GITHUB_PAT}:x-oauth-basic@github.com" > ~/.git-credentials'
                    sh "git clone --branch ${GIT_BRANCH} ${GIT_REPO}"
                }
            }
        }

        stage('Load Credentials') {
            steps {
                withCredentials([
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

        stage('Build and Deploy') {
            steps {
                // Use Docker Compose to build and start the services, using the .env file for configuration
                sh 'docker-compose up --build -d'
            }
        }
    }

    post {
        always {
            script {
                sh 'rm -f .env'
            }
        }
    }
}
