pipeline {
    agent any

    environment {
        GITHUB_PAT = credentials('GITHUB_PAT')
        EC2_DIRECTORY_PATH = credentials('EC2_DIRECTORY_PATH')
        GIT_BRANCH = 'development-junwei' // Set your desired branch here or make it a parameter
    }

    stages {

        stage('Update Directory on EC2') {
            steps {
                script {
                    // Configure Git to use the cached credentials helper
                    sh 'git config --global credential.helper cache'
                    sh 'git config --global credential.helper "cache --timeout=3600"'
                    // Write the GitHub PAT to the Git credentials file
                    sh 'echo "https://${GITHUB_PAT}:x-oauth-basic@github.com" > ~/.git-credentials'
                    // Change to the directory where the repository is located and pull the latest changes
                   env.DIR = EC2_DIRECTORY_PATH

                    // Change to the directory using a safe method
                    dir(env.DIR) {
                        sh 'git init'  // Ensure git is initialized in the directory
                        sh 'git remote add origin https://${GITHUB_PAT}@github.com/Amabellzq/SSD-Team-25.git || true'  // Add remote repository if not already added
                        sh 'git fetch origin'  // Fetch the latest changes
                        sh "git reset --hard origin/${env.GIT_BRANCH}"  // Reset the working directory to match the latest changes from the specified branch
                    }
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
