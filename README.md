# SSD-Team-25
## Prerequisites

Before you begin, ensure you meet the following requirements:

- **Software**:
  - Pycharm Professional / Visual Studio Code 
  - Docker installed and running.
  - PuTTY for Windows users needing SSH access
  - MySQL Workbench (Optional)

### Step 1: Setting Up PuTTY for SSH Access

1. **Generate SSH Keys with PuTTYgen**:
   - Open PuTTYgen from the Start menu.
   - Follow the instructions here to generate .ppk file:
     https://www.puttygen.com/convert-pem-to-ppk#Converting_Pem_to_Ppk_on_Windows
2. **Configure SSH Session in PuTTY**:
   - Open PuTTY and enter your server's IP address or hostname in the `Host Name` field.
   - Go to `Connection > SSH > Auth > Credentials` and browse to select your `.ppk` file for authentication.
   - Go back to `Session`, save the session by giving it a name, and then click `Open` to connect.

### Step 2: Configure SSH Tunnels

1. **Navigate to SSH Tunnels**: In the PuTTY configuration window, expand the `SSH` category in the left-hand menu and select `Tunnels`.

2. **Add a New Forwarded Port**:
   - **Source Port**: Enter `3307` (or any other local port you prefer that is not currently in use).
   - **Destination**: Enter `localhost:3306` (which is the default port for MySQL on the server).
   - Click the `Add` button. This action maps your local port `3307` to the remote port `3306` over SSH.


## Configuring the .env File

The `.env` file is used to set environment variables that configure how the application behaves differently depending on the environment (development, staging, production, etc.).

1. **Create a .env file** at the root of your project directory.
2. **Add the following variables** :
### Database configuration
```
DB_USER=sqluser
DB_PASSWORD=ICT2216_Grp25SSD
DB_HOST=host.docker.internal
DB_NAME=ICT2216_Database
DB_PORT=3307
```
**Note: In order to establish connection to the MYSQL on AWS EC2, Putty session must be running to enable SSH Tunnel**

## Running the application
1. Start Docker Compose:
```
docker-compose up --build
```
3. Access the website via `http://localhost:8080/`

## [Optional] Configure MySQL Workbench Access
1. Start a new connection
2. Fill up the below credential
```
Connection Name: SSD ICT2216 Database
Connection Method: Standard (TCP/IP)
Hostname: 127.0.0.1
Port: 3307
Username: sqluser
Password: ICT2216_Grp25SSD
```
**Note: In order to establish connection to the MYSQL on AWS EC2, Putty session must be running to enable SSH Tunnel**


