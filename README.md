# minio_manual

## Table of Conetents
- [Install docker](#install-docker)
- [Install minio as container](#install-minio-as-container)
- [Enable network encryption](#enable-network-encryption)
- [Install python SDKs](#install-python-sdks)
- [Deploy Minio KMS as container](#deploy-minio-kms-as-container)
- [Enable server side encryption with minio KMS](#enable-data-encryption-server-side-encryption---sse)

## Install docker
1. Set up Docker's `apt` repository
    ```bash
    # Add Docker's official GPG key:
    sudo apt update
    sudo apt install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
    Types: deb
    URIs: https://download.docker.com/linux/ubuntu
    Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
    Components: stable
    Signed-By: /etc/apt/keyrings/docker.asc
    EOF

    sudo apt update
    ```

2. Install docker packages
    ```bash
    sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    ```

3. Verify installation successful
    ```bash
    sudo docker run hello-world
    ```

    Output should be
    ```bash
    Hello from Docker!
    This message shows that your installation appears to be working correctly.

    To generate this message, Docker took the following steps:
    1. The Docker client contacted the Docker daemon.
    2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
        (amd64)
    3. The Docker daemon created a new container from that image which runs the
        executable that produces the output you are currently reading.
    4. The Docker daemon streamed that output to the Docker client, which sent it
        to your terminal.

    To try something more ambitious, you can run an Ubuntu container with:
    $ docker run -it ubuntu bash

    Share images, automate workflows, and more with a free Docker ID:
    https://hub.docker.com/

    For more examples and ideas, visit:
    https://docs.docker.com/get-started/
    ```


## Install minio as container
1. Pull the latest stable image of AIStor Server 
    ```bash
    sudo docker pull quay.io/minio/aistor/minio
    ```

2. Create directories for data and certificates. The following example uses `$HOME/minio` as the base path.
    ```bash
    mkdir -p $HOME/minio/data $HOME/minio/certs
    ```

3. Retrieve your license file 
    - go to [Minio pricing page](https://min.io/pricing?_gl=1*bglanp*_up*MQ..*_ga*MTU5ODUxOTQ0OC4xNzc0MTA4Nzcx*_ga_EHESQ21MLT*czE3NzQxMDg3NzAkbzEkZzAkdDE3NzQxMDg3NzAkajYwJGwwJGgw)

    - Click `Get Started` at `Free` tier. Give required information and the license will be sent to inserted email

4. Move licese to `$HOME/minio`
    ```bash
    mv ~/Downloads/minio.license ~/minio/
    ```

5. Check
    ```bash
    ls ~/minio/
    # output should be
    # certs  data  minio.license
    ```

## Enable Network Encryption
1. Load binary file for linux AMD64
    ```bash
    ~
    curl -L https://github.com/minio/certgen/releases/latest/download/certgen-linux-amd64 -o certgen
    ```

2. Make it executable
    ```bash
    sudo chmod +x certgen
    ```

3. Move to system path (optional)
    ```bash
    sudo mv certgen /usr/local/bin/
    ```

4. Generate certificates 
    ```bash
    cd ~/minio/certs
    certgen -host "localhost,127.0.0.1, <additional IP>"
    ```
    `additional IP` : minio's server IP
    ```bash
    ls
    # output should be
    # private.key  public.crt
    ```

5. Run MinIO AIStor with TLS 
    ```bash
    docker run -dt                                             \
    -p 9000:9000 -p 9001:9001                                \
    -v $HOME/minio/data:/mnt/data                            \
    -v $HOME/minio/certs:/etc/minio/certs                    \
    -v $HOME/minio/minio.license:/minio.license              \
    --name "aistor-server"                                   \
    quay.io/minio/aistor/minio:latest minio server /mnt/data \
    --license /minio.license                                 \
    --certs-dir /etc/minio/certs
    ```

6. Trust additional certificate authorities 

    If you need MinIO AIStor to trust certificates from additional certificate authorities, such as when connecting to `MinIO KMS` with self-signed certificates, place the CA certificates in the `$HOME/minio/certs/CAs` directory.

    ```bash
    mkdir -p $HOME/minio/certs/CAs
    cp /path/to/ca-certificate.crt $HOME/minio/certs/CAs/
    ```

    When you start the container, the CA certificates are mounted to `/etc/minio/certs/CAs` and automatically trusted by MinIO AIStor.

7. Install mc
    ```bash
    curl --progress-bar -L https://dl.min.io/aistor/mc/release/linux-amd64/mc -o mc
    chmod +x ./mc
    sudo mv ./mc /usr/local/bin/
    mc --version
    ```

8. Connect using HTTPS 
    Configure mc to trust the certificate 
    ```bash
    mkdir -p ~/.mc/certs/CAs
    cp $HOME/minio/certs/public.crt ~/.mc/certs/CAs/
    ```

    Then create an alias using HTTPS:
    ```bash
    mc alias set <alias_name> https://<server IP>:9000 minioadmin minioadmin
    ```
    - `alias_name` : can name it what ever you want but if the same name is set, last name will be keep.
    - `server IP` : IP of server that you want to connect.

9. Test connection
    ```bash
    mc admin info <alias_name>
    ```

    output should be
    ```bash
    ╭───────────────────────────────────────────────╮                                                         
    │  MinIO Cluster: ● Online  │  Edition: AIStor  │                                                         
    ╰───────────────────────────────────────────────╯                                                         
                                                                                                            
    Capacity                                                                                                  
    ╭──────────────────────────────────────────────────────────────────────────────╮                          
    │  Used:  25 GiB / 207 GiB  [█████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]  12.2%  │                          
    │  Free:  182 GiB                                                              │                          
    ╰──────────────────────────────────────────────────────────────────────────────╯                          
                                                                                                            
    Servers                                                                                                   
    ╭────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │  ●  localhost:9000★  │  Uptime: 1 hour   │  Drives: 1/1  │  Pool: 1  │  Version: 2026-03-20T23:11:32Z  │
    ╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯
                                                                                                            
    Pools                                                                                                     
    ╭─────────────────────────────────────────────────────╮                                                   
    │  Pool  │  Usage            │  Stripe Size  │  Sets  │                                                   
    │  1st   │  12.2% (207 GiB)  │  1            │  1     │                                                   
    ╰─────────────────────────────────────────────────────╯                                                   
                                                                                                            
    Data Summary                                                                                              
    ╭───────────────────────────────────────────────────────────────────────────────────────────────────────╮ 
    │  Used: 0 B  │  Objects: 0  │  Delete Markers: 0  │  Drives: 1 online / 0 offline  │  Erasure Code: 0  │ 
    ╰───────────────────────────────────────────────────────────────────────────────────────────────────────╯ 
    ```


## Install python SDKs
There are 2 ways to install
1. Virtual environment
    ```bash
    # create environment
    python3 -m venv minio-env
    # active it
    source minio-env/bin/activate
    # install lib
    pip install minio
    ```

2. Directly install
    ```bash
    pip install minio --break-system-packages
    ```

## Enable data encryption (Server side encryption - SSE)
<!-- 1. Insatll `KMS` image
```bash
sudo docker pull minio/kes
```

2. Install the KES CLI (Linux amd64)
```bash
# Download the KES binary
curl -L https://github.com/minio/kes/releases/latest/download/kes-linux-amd64 -o kes

# Make it executable
chmod +x kes

# Move it to your system path
sudo mv kes /usr/local/bin/

# check
kes --version
```

3.  -->


<!-- ## Deploy Minio KMS as container
1. Pull the latest stable image of MinIO KMS 
    ```bash
    sudo docker pull quay.io/minio/aistor/minkms
    ```

2. Create directory structure 
    ```bash
    mkdir -p ${HOME}/minkms/{data,certs}
    ```

3. Create certificates
    ```bash
    cd ${HOME}/minkms/certs
    certgen --host "localhost, 127.0.0.1"
    ```

4. Create a file at `${HOME}/minkms/config.yaml` with the following content:
    ```bash
    version: v1
    tls:
    certs:
    - key: /etc/minkms/certs/private.key
        cert: /etc/minkms/certs/public.crt
    ```

5. Create a file at `${HOME}/minkms/minkms.env` with the following content:
    ```bash
    MINIO_KMS_HSM_KEY=hsm:aes256:KEYVALUE
    MINIO_KMS_VOLUME=/mnt/minio-kms
    ```

    ```bash
    # generate a new key
    sudo docker run --rm quay.io/minio/aistor/minkms:latest --soft-hsm
    ```

    Replace the `KEYVALUE` with the command output.

6. Start the MinIO KMS server 
    ```bash
    sudo docker run \
    --name minio-kms \
    -p 7373:7373 \
    -v ${HOME}/minkms/certs:/etc/minkms/certs \
    -v ${HOME}/minkms/config.yaml:/etc/minkms/config.yaml \
    -v ${HOME}/minkms/data:/mnt/minio-kms \
    --env-file ${HOME}/minkms/minkms.env \
    quay.io/minio/aistor/minkms:latest \
    server /mnt/minio-kms --config /etc/minkms/config.yaml
    ```

    output should be
    ```bash
    2026-03-22 07:09:58 INFO  Starting server instance...

    Version        2025-11-12T19-14-51Z commit=affbaed7566108e6b63587526a41e19bccaa4474
    HSM            hsm:minio:soft
    Cluster        ID      93bb3ba0-bcb2-49a2-b66e-4856cf347066
                Node 0: 172.17.0.2:7373 <-

    Documentation  Web: https://docs.min.io/enterprise/aistor-key-manager
                CLI: $ minkms help

    Endpoint       https://172.17.0.2:7373
    API Key        k1:bZIISelEX21ipB0mKJMO0wGQ-xcEDJgLkN6Oz96EziQ

    => Server is up and running...
    ```

    You can optionally add the `run -d` flag to run the container in the background (detached mode).
    ```bash
    # delete previous container
    sudo docker rm minio-kms

    sudo docker run -d \
    --name minio-kms \
    -p 7373:7373 \
    -v ${HOME}/minkms/certs:/etc/minkms/certs \
    -v ${HOME}/minkms/config.yaml:/etc/minkms/config.yaml \
    -v ${HOME}/minkms/data:/mnt/minio-kms \
    --env-file ${HOME}/minkms/minkms.env \
    quay.io/minio/aistor/minkms:latest \
    server /mnt/minio-kms --config /etc/minkms/config.yaml
    ```

    The output includes the root API Key as `k1:VALUE`. If you run the container in a detached mode, use the `docker logs` command to retrieve the API key. Save the value to a secure location for use in the next steps.
    ```bash
    sudo docker logs minio-kms
    ```

    >note:
    >`VALUE` is used in later step

7. Install MinIO KMS Server (`minkms` binary)
    ```bash
    # 1. Download with a specific filename to avoid the folder conflict
    curl -L https://dl.min.io/aistor/minkms/release/linux-amd64/minkms -o minkms-bin

    # 2. Make it executable
    chmod +x minkms-bin

    # 3. Use sudo to move it and rename it to 'minkms' in the system path
    sudo mv minkms-bin /usr/local/bin/minkms

    # 4. Verify it works
    minkms --version
    ```

8. Connect to the MinIO KMS server. 
    ```bash
    export MINIO_KMS_ENDPOINT=http://localhost:7373
    export MINIO_KMS_API_KEY=k1:VALUE
    minkms stat -k
    ```

    >note: 
    >`VALUE` get from step 6

    output should be
    ```bash
    ●  Node 0 at 172.17.0.2:7373
    Version     2025-11-12T19-14-51Z
    Uptime      24m31s
    HSMs        1
    Commit      0
    State       Leader
    Leader      Node 0
    Heartbeat   233ms ago
    System
        OS       linux
        CPUs     4 amd64
        Memory   4.20MiB
    ```

 9. Create an enclave and identity for AIStor 
    
    Run the following commands to generate the necessary resources. Change `object-store-name` (`alias`) to reflect the name or label you want to associate with AIStor.
    ```bash
    export MINIO_KMS_SERVER=127.0.0.1:7373
    minkms add-enclave -k <object-store-name>
    minkms add-identity -k --enclave <object-store-name> --admin
    ```

    **Test**
    - `object-store-name` : myhp

    The command returns the API Key and Identity for use with AIStor. Copy the `k2:` prefixed value for use when enabling AIStor Server-Side Encryption.

    Output
    ```bash
    Your API key:

    k2:bQUODAKbVSj2PYWP5rBWTvuVnAbS7ktaAs2XsGScRwI

    This is the only time it is shown. Keep it secret and secure!

    Your API key's identity:

    h1:Vic9BzjKXEheV-bgEy2INHJt56TepoTZ_4Y32IqE9Ok

    The identity is not a secret and can be shared securely.
    Peers need your identity in order to verify your API key.

    This identity can be re-computed again via:

    $ minkms identity k2:bQUODAKbVSj2PYWP5rBWTvuVnAbS7ktaAs2XsGScRwI

    Added identity to server successfully.
    ```
    

## Server Side Encryption with MinIO KMS

### Prerequisites 
- Network encryption (TLS) 
- MinIO KMS 
- Utilities : `base64` and `yq`
    ```bash
    # isntall yq 
    sudo wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/local/bin/yq &&\
    
    sudo chmod +x /usr/local/bin/yq
    ```

    ```bash
    # check
    base64 --version
    yq --version
    ```

### Prodecure -->
