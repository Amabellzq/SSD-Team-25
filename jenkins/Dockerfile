FROM jenkins/jenkins:lts

USER root

# Set the Jenkins options to use the specified port and prefix
ENV JENKINS_OPTS="--httpPort=8080 --prefix=/jenkins"

RUN apt-get update && \
    apt-get install -y docker.io sudo && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Ensure Jenkins user has access to Docker
RUN usermod -aG docker jenkins

# Switch to Jenkins user and install the BlueOcean plugin with all dependencies
USER jenkins

# Install plugins using jenkins-plugin-cli
RUN jenkins-plugin-cli --plugins \
    blueocean \
    git \
    github-branch-source \
    pipeline-model-definition \
    docker-workflow \
    workflow-aggregator \
    credentials-binding \
    gitlab-plugin \
    token-macro \
    json-path-api

# Switch back to root to set up Docker-in-Docker permissions
USER root

# Add the Jenkins user to the Docker group
RUN usermod -aG docker jenkins

# Switch to Jenkins user to finish the setup
USER jenkins
