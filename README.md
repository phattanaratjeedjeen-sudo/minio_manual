# minio_manual

<!-- 
## Table of Conetents

1. Insatll `KMS` image
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


 ## Deploy Minio KMS as container
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
    ``

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

    Y
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

### Prodecure  -->


## Deploy MinIO on linux
1. Install minio server
    ```bash
    # for AMD64
    curl --progress-bar -L dl.min.io/aistor/minio/release/linux-amd64/minio.deb -o minio.deb
    sudo dpkg -i minio.deb
    ```

2.  Retrieve your license file 

    Get lincese [here](https://www.min.io/pricing)

    ```bash
    sudo mkdir /opt/minio
    sudo touch /opt/minio/minio.license
    sudo chown -R minio-user:minio-user /opt/minio
    ```

3.  Create the directory for the data 
    ```bash
    sudo mkdir -p /mnt/drive-1/minio
    ```

4. Configure the Environment File
    ```bash
    sudo nano /etc/default/minio
    ```

    Paste the exact configuration from the documentation:
    ```bash
    # Path to the license file provided by MinIO Subnet
    MINIO_LICENSE="/opt/minio/minio.license"

    # Data directory for a Single-Node Single-Drive setup
    MINIO_VOLUMES="/mnt/drive-1/minio"

    # Server options (Ports and UI)
    MINIO_OPTS="--address :9000 --console-address :9001"

    # Root credentials (Change these for production)
    MINIO_ROOT_USER=minioadmin
    MINIO_ROOT_PASSWORD=minioadmin
    ```

5. Ensure MinIO AIStor has ownership of associated folders and drives. 
    ```bash
    sudo chown -R minio-user:minio-user /opt/minio/
    sudo chown -R minio-user:minio-user /mnt/drive-1/minio
    ```

6. Enable and start the MinIO AIStor deployment. 
    ```bash
    sudo systemctl enable minio.service
    sudo systemctl start minio.service
    ```

    ```bash
    # check
    sudo systemctl status minio.service 
    ```

## Configure TLS Network Encryption
1. Create the certificates and Certificate Authorities (CAs) your environment requires.

2. Create the appropriate directories for your certificates and CAs.
    ```bash
    cd /opt/minio/
    sudo mkdir CAs
    sudo mkdir certs
    ```

3. Set the ownership of these directories to `minio-user`
    ```bash
    sudo chown -R minio-user:minio-user /opt/minio/certs
    ```

4. Add the default certificates to the `/certs` directory. At least one `private.key` and `public.crt` must be placed at the root of the `certs` directory, to provide the default certificate.
    ```bash
    /certs
        private.key
        public.crt
    ```

5. Modify the environment file at `/etc/default/minio`
    ```bash
    sudo gedit /etc/default/minio 
    ```

    copy and paste
    ```bash
    # 1. Lincese
    MINIO_LICENSE="/opt/minio/minio.license"

    # 2. Data Drive Directory
    MINIO_VOLUMES="/mnt/drive-1/minio"

    # 3. Network, Certificates
    MINIO_OPTS="--address :9000 --console-address :9001 --certs-dir /opt/minio/certs"

    # 4. Root Credentials 
    MINIO_ROOT_USER=minioadmin
    MINIO_ROOT_PASSWORD=minioadmin

    # 5. Server URL
    MINIO_SERVER_URL="https://192.168.1.152:9000"
    ```

6. Restart MinIO
    ```bash
    sudo systemctl restart minio.service 
    ```

## Install MinIO KMS on Linux

1.  Create a MinIO KMS system user and group
    ```bash
    sudo groupadd -r minkms-user
    sudo useradd -M -r -g minkms-user minkms-user
    ```

2. Create a directory structure for KMS files and configurations
    ```bash
    sudo mkdir -p /etc/minkms/certs/CAs /etc/minkms/config /mnt/minio-kms
    sudo touch /etc/default/minkms
    ```
    The command creates the following structure:
    ```bash
    /etc/minkms
        /certs             # Directory for TLS certificates
            /CAs           # Certificate Authority files for client verification
        /config            # KMS configurations

    /mnt/minio-kms         # Dedicated mounted volume for KMS data
    /etc/default/minkms    # Environment variables for MinKMS process
    ```

    Use `chown` and `chmod` to restrict access to these directories to only the `minkms-user` user and group.

    ```bash
    sudo chown -R minkms-user:minkms-user /etc/minkms
    sudo chmod -R 750 /etc/minkms
    sudo chown -R minkms-user:minkms-user /mnt/minio-kms
    sudo chmod -R 750 /mnt/minio-kms
    sudo chown -R minkms-user:minkms-user /etc/default/minkms
    sudo chmod -R 750 /etc/default/minkms
    ```

3.  Download the MinIO KMS binary
    ```bash
    curl --progress-bar --retry 10 -L https://dl.min.io/aistor/minkms/release/linux-amd64/minkms -o minkms
    chmod +x ./minkms
    sudo mv ./minkms /usr/local/bin/
    ```

    You can validate the installation by running `minkms help`

4. Add the TLS certificates and Certificate Authorities

    Place the TLS private key `private.key` and public certificate `public.crt` in the `/etc/minkms/certs` directory

    ```bash
    sudo cp -r /opt/minio/certs /etc/minkms/
    sudo chmod -R 600 /etc/minkms/certs
    ```

5. Create a service file for MinIO KMS

    Create a new `minkms.service` file at `/usr/lib/systemd/system/minkms.service` with the following content:

    ```bash
    sudo touch /usr/lib/systemd/system/minkms.service
    sudo nano /usr/lib/systemd/system/minkms.service
    ```

    ```bash
    [Unit]
    Description=MinKMS
    Documentation=https://docs.min.io/enterprise/aistor-key-manager
    Wants=network-online.target
    After=network-online.target
    AssertFileIsExecutable=/usr/local/bin/minkms
    [Service]
    WorkingDirectory=/usr/local
    User=minkms-user
    Group=minkms-user
    ProtectProc=invisible
    EnvironmentFile=-/etc/default/minkms
    ExecStart=/usr/local/bin/minkms server $MINIO_KMS_VOLUME $MINIO_KMS_OPTS
    # Let systemd restart this service always
    Restart=always
    # Specifies the maximum file descriptor number that can be opened by this process
    LimitNOFILE=65536
    # Specifies the maximum number of threads this process can create
    TasksMax=infinity
    # Disable timeout logic and wait until process is stopped
    TimeoutStopSec=infinity
    SendSIGKILL=no
    [Install]
    WantedBy=multi-user.target
    # Built for ${project.name}-${project.version} (${project.name})
    ```

6. Generate an HSM Key
    MinIO KMS uses a hardware/software security module (HSM) for en/decrypting the keystore and for authenticating internode cals
    ```bash
    minkms --soft-hsm
    ```
    ```bash
    # output
    Your software HSM key:

        cd hsm:aes256:uPG5uo2QPzPgygxIOWO8h/AqBgtORlViR3WP32qS0xo=

    This is the only time it is shown. Keep it secret and secure!

    The HSM protects your KMS cluster as unseal mechanism by decrypting the
    internal root encryption key ring.
    Please store it at a secure location. For example, your password manager.
    Without your HSM key you cannot decrypt any data within your KMS cluster.
    ```

7. Build an environment file for MinIO KMS
    Open the file at `/etc/default/minkms` and enter the following content:
    ```bash
    cd /etc/default/
    sudo gedit minkms
    ```
    ```bash
    MINIO_KMS_HSM_KEY=hsm:aes256:KEYVALUE
    MINIO_KMS_VOLUME=/mnt/minio-kms
    MINIO_KMS_OPTS="--config /etc/minkms/config.yaml"
    ```

8. Create a file at `/etc/minkms/config.yaml` with the following content:
    ```bash
    version: v1
    tls:
    certs:
        - key: /etc/minkms/certs/private.key
        cert: /etc/minkms/certs/public.crt
    ca: /etc/minkms/certs/CAs
    datastore:
    path: /mnt/minio-kms
    ```

    ```bash
    sudo chmod 750 /etc/minkms
    sudo chmod 640 /etc/minkms/config.yaml
    ```

9. Enable and start the MinIO KMS service   
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable minkms
    sudo systemctl start minkms
    ```

    ```bash
    # validate the status and output of MinIO KMS
    sudo journalctl -u minkms
    ```

    You can also filter the `journactl` output to only return the `root` or superadmin API Key:

    ```bash
    journalctl -u minkms -g "API Key" -o cat --output-fields "MESSAGE"
    ```

10. Create an enclave and identity for AIStor Object Store

    Each Object Store requires an enclave and identity for accessing MinIO KMS and performing cryptographic operations.

    ```bash
    export MINIO_KMS_SERVER=127.0.0.1:7373
    minkms add-enclave -k -a k1:`API key` object-store-name
    minkms add-identity -k -a k1:`API key` --enclave object-store-name --admin
    ```
    `API key`: get from previous step
    
    Change the `object-store-name` to reflect the name or label you want to associate with the object store.


## Server Side Encryption with MinIO KMS

1. Add MinIO KMS settings to the environment file

    Open the `/etc/default/minio`
    ```bash
    sudo gedit /etc/default/minio
    ```
    
    Add following line
    ```bash
    MINIO_KMS_SERVER=""
    MINIO_KMS_SSE_KEY=""
    MINIO_KMS_ENCLAVE=""
    MINIO_KMS_API_KEY=""
    ```

    How to check
    ```bash
    # MINIO_KMS_SERVER
    sudo systemctl status minkms

    # MINIO_KMS_API_KEY
    journalctl -u minkms -g "API Key" -o cat --output-fields "MESSAGE"

    # MINIO_KMS_ENCLAVE
    minkms ls-enclave   
    ```

2. Trust certificate and restart 

    ```bash
    sudo cp /opt/minio/certs/public.crt /usr/local/share/ca-certificates/minio-kms.crt

    sudo update-ca-certificates

    sudo systemctl restart minio
    ```

<!-- ## Key SSE structure

| name  | stored in | description |
| --- | --- | --- | 
| master key  | KMS (enclave) |  |
| KEK | volatile memory | 
| DEK | object's metadata | -->

## SSE key operation
```bash
# create SSE name `key-v1`
mc admin kms key create myhp key-v1 --json
```
```bash
# remove key with specific version
minkms rm-key -k -e hp-enclave --version 1 key-v1
```

```bash
# list SSE key
minkms ls-key -e hp-enclave
# or
mc admin kms key list myhp/
```

```bash
# Check current SSE used
mc stat myhp/a-buck/SSE_key.txt
```

## Ways to enable SSE 
- Global level
    ```bash
    sudo gedit /etc/default/minio 
    # and edit at `MINIO_KMS_SSE_KEY`
    ```

- Bucket level
    ```bash
    mc encrypt set sse-kms key-v1 myhp/b-buck/
    ```

## Key Rotation 
>note:
>read more information about [Batch Key Rotation](https://docs.min.io/enterprise/aistor-object-store/operations/batch-key-rotation/)
### Types
1. Scheduled Rotation (Master Key)
    - Create new key version
    - New data: locked by new key
    - Old data: locked by old key, KMS stores old key to decryp old data only

2. Re-encryption / Batch Rotation (file's key)
    - Decypt old file with old key and encryp new with new key
    - All date: use new key
    - Bucket level: still use old key

### Example
- Scheduled Rotation
    ```bash
    minkms add-key -k -e hp-enclave --version key-v1
    # view least key version 
    minkms stat-key -e hp-enclave --json key-v1
    ```

- Batch Rotation
    ```bash
    # create batch file
    gedit rotate.yaml
    ```

    copy this into batch file

    ```bash
    keyrotate:
    apiVersion: v1
    # destination bucket
    bucket: a-buck
    prefix: ""          
    encryption:
        # new key
        key: key-v1
    flags:
        filter:
        plaintextOnly: false
        # change only file that used this key
        kmskey: "object-store-primary-default-key" 
        retry:
        attempts: 5
        delay: "500ms"
    ```

    ```bash
    mc batch start myhp <path-to-rotate.yaml>
    ```
