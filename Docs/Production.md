# 🚀 Deploying to Production

## VPS (Virtual Private Server)
- VPS hosting is a service that provides users with virtual machines running on a physical server, each with dedicated virtual resources, its own operating system, and independent configuration. [1](https://www.hostinger.com/tutorials/what-is-vps-hosting)
- There are several service providers in different budget and technical needs. In this case, we use a "Cloud VPS 20" package from [Contabo](https://contabo.com/en/vps/) that offer Linux VPS with full root access.
    > The specifications of this package are:
    > - Cores: 6 vCPU Cores
    > - Memory: 12 GB RAM
    > - Storage: 100 GB NVMe (or 200 GB SSD)
    > - Snapshots: 2 Snapshots
    > - Port Speeds up to 1 Gbit/s: 300 Mbit/s Port
- When you purchase this service, login to the system and it will show the detail of your IP address, host and others.
**Don't forget to copy the root password, this will use for the first authentication**

## Server setup & SSH Access
- Firstly, when you begin to start config the server, you have to connect using SSH (Secure Shell) protocol. Use text-based interface liked Command Prompt or Windows Powershell to config.
- Before connecting to a server, you should have an SSH key for an authentication with a cryptographic key pair instead of a password. It will more secure.
- The key pair contains: Private key which stays on your machine; and Public key is on the server.
    1. Connecting to the server with the default root user and password
    ```
    ssh root@YOURHOSTIPADDRESS
    ```
        This is the first connection, which means a host isn't established. It will ask "Are you sure you want to continue connecting (yes/no/[fingerprint]), type "yes" then it required to type a password.
    
    2. Create a new user and modify into the server
    ```
    adduser NEWUSERNAME
    usermod -aG sudo NEWUSERNAME
    ```
    - The system will require to create a new password - type and confirm it.
    - It will have a user information form, you have unnecessary to do it - just "Enter" and type "Y"

    3. Generate (or locate) an SSH key pair on your local machine
    ```
    ssh-keygen -t ed25519
    # View/copy your public key:
    cat ~/.ssh/id_ed25519.pub
    ```
    - On the server, add the public key to the new user's `authorized_keys`:
    ```
    sudo install -d -m 700 /home/NEWUSERNAME/.ssh
    sudo nano /home/NEWUSERNAME/.ssh/authorized_keys
    ```
    * Copy the public key and paste into an authorized_keys file, save and exit.

    4. Modify the elements: Permissions and owner
    ```
    sudo chmod 700 /home/NEWUSERNAME/.ssh
    sudo chmod 600 /home/NEWUSERNAME/.ssh/authorized_keys
    sudo chown -R NEWUSERNAME:NEWUSERNAME /home/NEWUSERNAME/.ssh
    ```

    5. Config the server authentication
    ```
    sudo nano /etc/ssh/sshd_config
    ```
    - Find the parameters in this file and set the config:
        **PasswordAuthentication no** # Disable password authentication
        **PermitRootLogin no** # Block root login
        **PubkeyAuthentication yes** # Keys are the only allowed method
    - When you finish, save and exit

    6. Restart the server
    ```
    sudo systemctl restart ssh
    ```
    
    7. Reconnect with your SSH key
    ```
    ssh NEWUSERNAME@YOURIPADDRESS
    ```
    - Now, you can connect without password

## Domain or Dynamic DNS
- Now, you have only IP address but in general you should have an address name for user recognization. Therefore, we should create our own hostname. In this case, we register with a free dynamic DNS hosted named [DuckDNS](https://www.duckdns.org/), it will give us a stable public hostname for our IP address.

## Docker
- Docker is an application that simplifies the process of managing application processes in containers. Containers let you run your applications in resource-isolated processes. They are similar to virtual machines, but containers are more portable, more resource-friendly, and more dependent on the host operating system.
- As this server runs on Ubuntu 24.04, so we install Docker with a tutorial from [DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04)
    1. Installing Docker
        - Update latest packages list
        ```
        sudo apt update
        ```
        - Install a few packages for using packages over HTTPS with `apt`
        ```
        sudo apt install ca-certificates curl gnupg
        ```
        - Add the GPG key from Docker official to the system
        ```
        sudo install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        sudo chmod a+r /etc/apt/keyrings/docker.gpg
        ```
        - Add the Docker repository to APT sources. (It automatically detects your Ubuntu version)
        ```
        echo \
          "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
          $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
          sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        ```
        - Update the packages with your newly Docker packages
        ```
        sudo apt update
        ```
        - Verify that you are install from the Docker repository instead of the default Ubuntu
        ```
        apt-cache policy docker-ce
        ```
        - Finally, install the Docker
        ```
        sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        ```
    - Now, Docker has installed. Run this command to check if it's running or not:
    ```
    sudo systemctl status docker
    ```

    2. Executing the Docker Command Without `sudo`
    - By default, the docker command can only be run the root user or by a user in the docker group, which is automatically created during Docker’s installation process.
    - If you want to avoid typing `sudo` whenever you run the docker command:
        * Add user to the docker group
        ```
        sudo usermod -aG docker ${USER}
        su - ${USER}
        ```
        * Run this command to confirm that your username is now added to the group
        ```
        groups
        ```
        * Add a user to the Docker group
        ```
        sudo usermod -aG docker NEWUSERNAME
        ```
- When you finish installing Docker, create a docker compose file
```
sudo nano docker-compose.yml
```
- We use a docker service from [Caddy](https://github.com/lucaslorentz/caddy-docker-proxy)
- Complete the service detail with your hostname from DuckDNS:
```
services:
  whoami:
    image: traefik/whoami
    networks:
      - caddy
    labels:
      caddy: whoami.YOURNAME.duckdns.org
      caddy.reverse_proxy: "{{upstreams 80}}"

networks:
  caddy:
    external: true
```

## Reverse Proxy
- A reverse proxy is a server that sits in front of web servers and forwards client (e.g. web browser) requests to those web servers. Reverse proxies are typically implemented to help increase security, performance, and reliability. [2](https://www.cloudflare.com/learning/cdn/glossary/reverse-proxy/)
    1. Create a path and a docker compose file
    ```
    sudo mkdir -p /opt/docker && cd /opt/docker
    sudo nano docker-compose.yml
    ```
    2. Place the config details from Caddy
    ```
    services:
        caddy:
            image: lucaslorentz/caddy-docker-proxy:ci-alpine
            ports:
                - 80:80
                - 443:443/tcp
                - 443:443/udp
            environment:
                - CADDY_INGRESS_NETWORKS=caddy
            networks:
                - caddy
            volumes:
                - /var/run/docker.sock:/var/run/docker.sock
                - caddy_data:/data
            restart: unless-stopped

    networks:
        caddy:
            external: true

    volumes:
        caddy_data: {}
    ```

## Git Branch Strategy
- In default, when we create a Github repository, it will create a main branch. In addition, if there are many contributors in each repo, they should create their own branch for their coding.
> The main concepts of production are:
> 1. Never push directly to "prod" - always merge from "main"
> 2. Before merging to "prod", you should use pull requests to review code first
> 3. The webhook fires only on pushes to "prod"
- To deploy on production, we create a new branch named "prod" for production
```
git checkout -b prod
git push -u origin prod
```

## Firewall
- A firewall is a security system that monitors and controls network traffic based on a set of security rules. [3](https://www.cloudflare.com/learning/security/what-is-a-firewall/)
- UFW (uncomplicated firewall) is a command-line tool designed to simplify firewall management on Linux systems, particularly those based on Ubuntu. [4](https://www.digitalocean.com/community/tutorials/ufw-essentials-common-firewall-rules-and-commands)
    1. Allow SSH before enabeling UFW
    ```
    sudo ufw allow ssh
    ```
    2. Enable UFW (If not already on)
    ```
    sudo ufw enable
    ```
    3. Allow HTTP and HTTPS
    ```
    sudo ufw allow HTTP
    sudo ufw allow HTTPS
    ```
    * Check the rules are in place
    ```
    sudo ufw status verbose
    ```