pipeline {
    agent any

    environment {
        SECRET_KEY = credentials('SECRET_KEY')
        MYSQL_ROOT_PASSWORD = credentials('MYSQL_ROOT_PASSWORD')
        MYSQL_DATABASE = credentials('MYSQL_DATABASE')
        MYSQL_ADMIN_USER = credentials('MYSQL_ADMIN_USER')
        MYSQL_ADMIN_PASSWORD = credentials('MYSQL_ADMIN_PASSWORD')
        MYSQL_USER = credentials('MYSQL_USER')
        MYSQL_USER_PASSWORD = credentials('MYSQL_USER_PASSWORD')
        MYSQL_READONLY_USER = credentials('MYSQL_READONLY_USER')
        MYSQL_READONLY_PASSWORD = credentials('MYSQL_READONLY_PASSWORD')
        MYSQL_HOST = credentials('MYSQL_HOST')
        SERVER_DOMAIN_OR_IP = credentials('SERVER_DOMAIN_OR_IP')
    }

    stages {
        stage('Build') {
            steps {
                script {
                    docker.compose(
                        file: 'docker-compose.prod.yml',
                        command: 'build'
                    )
                }
            }
        }
        stage('Deploy') {
            steps {
                script {
                    // Replace the placeholder in nginx.conf with the actual server IP
                    sh '''
                    sed -i 's/${SERVER_DOMAIN_OR_IP}/'${SERVER_DOMAIN_OR_IP}'/g' nginx.conf
                    '''

                    // Deploy the application
                    docker.compose(
                        file: 'docker-compose.prod.yml',
                        command: 'up -d'
                    )
                }
            }
        }
    }
}
