pipeline {
    agent any

    environment {
        SECRET_KEY = credentials('SECRET_KEY')
        MYSQL_ROOT_PASSWORD = credentials('MYSQL_ROOT_PASSWORD')
        MYSQL_DATABASE = credentials('MYSQL_DATABASE')
        MYSQL_ADMIN_USER = credentials('MYSQL_ADMIN_USER')
        MYSQL_ADMIN_PASSWORD = credentials('MYSQL_ADMIN_PASSWORD')
        MYSQL_MERCHANT_USER = credentials('MYSQL_MERCHANT_USER')
        MYSQL_MERCHANT_PASSWORD = credentials('MYSQL_MERCHANT_PASSWORD')
        MYSQL_USER = credentials('MYSQL_USER')
        MYSQL_USER_PASSWORD = credentials('MYSQL_USER_PASSWORD')
        MYSQL_READONLY_USER = credentials('MYSQL_READONLY_USER')
        MYSQL_READONLY_PASSWORD = credentials('MYSQL_READONLY_PASSWORD')
        MYSQL_HOST = credentials('MYSQL_HOST')
        GITHUB_PAT = credentials('GITHUB_PAT')
        EC2_DIRECTORY_PATH = credentials('EC2_DIRECTORY_PATH')
        GIT_BRANCH = 'development-junwei' // Set your desired branch here or make it a parameter
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    // Configure Git to use the cached credentials helper
                    sh 'git config --global credential.helper cache'
                    sh 'git config --global credential.helper "cache --timeout=3600"'
                    // Write the GitHub PAT to the Git credentials file
                    sh 'echo "https://${env.GITHUB_PAT}:x-oauth-basic@github.com" > ~/.git-credentials'
                }
                // Checkout the code from the private repository using the PAT and specified branch
                git url: 'https://github.com/Amabellzq/SSD-Team-25.git', branch: "${env.GIT_BRANCH}", credentialsId: 'GITHUB_PAT'
            }
        }

        stage('Update Directory on EC2') {
            steps {
                script {
                    // Configure Git to use the cached credentials helper
                    sh 'git config --global credential.helper cache'
                    sh 'git config --global credential.helper "cache --timeout=3600"'
                    // Write the GitHub PAT to the Git credentials file
                    sh 'echo "https://${env.GITHUB_PAT}:x-oauth-basic@github.com" > ~/.git-credentials'
                    // Change to the directory where the repository is located and pull the latest changes
                    dir("${env.EC2_DIRECTORY_PATH}") {
                        sh 'git init'  // Ensure git is initialized in the directory
                        sh 'git remote add origin https://${GITHUB_PAT}@github.com/Amabellzq/SSD-Team-25.git || true'  // Add remote repository if not already added
                        sh 'git fetch origin'  // Fetch the latest changes
                        sh "git reset --hard origin/${env.GIT_BRANCH}"  // Reset the working directory to match the latest changes from the specified branch
                    }
                }
            }
        }

        stage('Create Docker Secrets') {
            steps {
                script {
                    // Create Docker secrets from Jenkins credentials
                    sh 'echo "${SECRET_KEY}" | docker secret create secret_key -'
                    sh 'echo "${MYSQL_ROOT_PASSWORD}" | docker secret create mysql_root_password -'
                    sh 'echo "${MYSQL_DATABASE}" | docker secret create mysql_database -'
                    sh 'echo "${MYSQL_ADMIN_USER}" | docker secret create mysql_admin_user -'
                    sh 'echo "${MYSQL_ADMIN_PASSWORD}" | docker secret create mysql_admin_password -'
                    sh 'echo "${MYSQL_MERCHANT_USER}" | docker secret create mysql_merchant_user -'
                    sh 'echo "${MYSQL_MERCHANT_PASSWORD}" | docker secret create mysql_merchant_password -'
                    sh 'echo "${MYSQL_USER}" | docker secret create mysql_user -'
                    sh 'echo "${MYSQL_USER_PASSWORD}" | docker secret create mysql_user_password -'
                    sh 'echo "${MYSQL_READONLY_USER}" | docker secret create mysql_readonly_user -'
                    sh 'echo "${MYSQL_READONLY_PASSWORD}" | docker secret create mysql_readonly_password -'
                    sh 'echo "${MYSQL_HOST}" | docker secret create mysql_host -'
                }
            }
        }

        stage('Build and Deploy') {
            steps {
                // Use Docker Compose to build and start the services, using Docker secrets for configuration
                sh 'docker-compose up --build -d'
            }
        }
    }

    post {
        always {
            // Clean up Docker secrets after usage
            sh 'docker secret rm secret_key mysql_root_password mysql_database mysql_admin_user mysql_admin_password mysql_merchant_user mysql_merchant_password mysql_user mysql_user_password mysql_readonly_user mysql_readonly_password mysql_host'
        }
    }
}
