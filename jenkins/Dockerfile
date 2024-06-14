FROM jenkins/jenkins:lts

USER root

# Set the Jenkins options to use the specified port and prefix
ENV JENKINS_OPTS="--httpPort=8080 --prefix=/jenkins"

# Install Docker CLI and other necessary tools
RUN apt-get update && apt-get install -y docker.io sudo

# Ensure Jenkins user has access to Docker
RUN usermod -aG docker jenkins

# Switch to Jenkins user and install the BlueOcean plugin
USER jenkins
RUN jenkins-plugin-cli --plugins blueocean

# Switch back to root to set up Docker-in-Docker permissions
USER root

# Add the Jenkins user to the Docker group
RUN usermod -aG docker jenkins

# Switch to Jenkins user to finish the setup
USER jenkins
