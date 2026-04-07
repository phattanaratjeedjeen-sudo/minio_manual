# Minio Manual
## Table of Contents
- [Deploy MinIO on Linux](#deploy-minio-on-linux)
- [Configure TLS Network Encryption](#configure-tls-network-encryption)
- [Install MinIO KMS on Linux](#install-minio-kms-on-linux)
- [Server Side Encryption with MinIO KMS](#server-side-encryption-with-minio-kms)
- [SSE Key Operation](#sse-key-operation)
- [File Structure](#file-structure)

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

### Ways to enable SSE 
- Global level
    ```bash
    sudo gedit /etc/default/minio 
    # and edit at `MINIO_KMS_SSE_KEY`
    ```

- Bucket level
    ```bash
    mc encrypt set sse-kms key-v1 myhp/b-buck/
    ```

### Key Rotation 
>note: 
>read more information about [Batch Key Rotation](https://docs.min.io/enterprise/aistor-object-store/operations/batch-key-rotation/)
#### Types
1. Scheduled Rotation (Master Key)
    - Create new key version
    - New data: locked by new key
    - Old data: locked by old key, KMS stores old key to decryp old data only

2. Re-encryption / Batch Rotation (file's key)
    - Decypt old file with old key and encryp new with new key
    - All date: use new key
    - Bucket level: still use old key

#### Example
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

## File Structure 
### Station (MinIO, MinKMS)
```bash
/opt/minio/                                # MinIO root directory
├── minio.license                          # License file (owner: minio-user, 644)
├── certs/                                 # MinIO TLS certificates (owner: minio-user, 750)
│   ├── private.key                        # PC1's MinIO private key (600)
│   ├── public.crt                         # PC1's MinIO certificate (644)
│   └── CAs/                               # Certificate Authorities (755)
│       ├── robot-public.crt               # Optional CA
│       └── kms-ca.crt                     # Optional: KMS CA for client validation
└── CAs/                                   # Alternative CA directory

/mnt/drive-1/minio/                        # Data storage (owner: minio-user, 755)
├── .minio.sys/                            # Internal metadata
└── [bucket-data]/                         # User buckets

/etc/default/minio                         # MinIO environment (644)
# Content:
# MINIO_LICENSE="/opt/minio/minio.license"
# MINIO_VOLUMES="/mnt/drive-1/minio"
# MINIO_OPTS="--address :9000 --console-address :9001 --certs-dir /opt/minio/certs"
# MINIO_SERVER_URL="https://192.168.1.152:9000"
# MINIO_ROOT_USER=minioadmin
# MINIO_ROOT_PASSWORD=minioadmin
# MINIO_KMS_SERVER="https://192.168.1.152:7373"
# MINIO_KMS_API_KEY="k2:YOUR_API_KEY"
# MINIO_KMS_ENCLAVE="object-store-pc1"

/etc/minkms/                               # MinIO KMS directory (owner: minkms-user, 750)
├── certs/                                 # KMS TLS certificates (owner: minkms-user, 600)
│   ├── private.key                        # KMS private key
│   ├── public.crt                         # KMS certificate (shared with PC2)
│   └── CAs/                               # Certificate Authorities
│       └── robot-public.crt
├── config.yaml                            # KMS configuration (owner: minkms-user, 640)
└── config/                                # KMS config directory

/mnt/minio-kms/                            # KMS data storage (owner: minkms-user, 750)
└── [KMS internal data]

/etc/default/minkms                        # KMS environment (owner: minkms-user, 750)
# Content:
# MINIO_KMS_HSM_KEY=hsm:aes256:KEYVALUE
# MINIO_KMS_VOLUME=/mnt/minio-kms
# MINIO_KMS_OPTS="--config /etc/minkms/config.yaml"

/usr/lib/systemd/system/minkms.service     # KMS systemd service (644)

/usr/local/bin/minkms                      # KMS binary (755)
```

### Robot (MinIO)
```bash
/opt/minio/                                # MinIO root directory
├── minio.license                          # License file (owner: minio-user, 644)
├── certs/                                 # MinIO TLS certificates (owner: minio-user, 750)
│   ├── private.key                        # PC2's MinIO private key (600)
│   ├── public.crt                         # PC2's MinIO certificate (644)
│   └── CAs/                               # Certificate Authorities (755)
│       ├── robot-public.crt               # Optional CA
│       └── kms-station.crt                # **IMPORTANT: KMS public cert from Station**
└── CAs/                                   # Alternative CA directory

/mnt/drive-1/minio/                        # Data storage (owner: minio-user, 755)
├── .minio.sys/                            # Internal metadata
└── [bucket-data]/                         # User buckets

/etc/default/minio                         # MinIO environment (644)
# Content:
# MINIO_LICENSE="/opt/minio/minio.license"
# MINIO_VOLUMES="/mnt/drive-1/minio"
# MINIO_OPTS="--address :9000 --console-address :9001 --certs-dir /opt/minio/certs"
# MINIO_SERVER_URL="https://192.168.1.153:9000"
# MINIO_ROOT_USER=minioadmin
# MINIO_ROOT_PASSWORD=minioadmin
# MINIO_KMS_SERVER="https://192.168.1.152:7373"    # <-- Points to Station's KMS
# MINIO_KMS_API_KEY="k2:YOUR_API_KEY"
# MINIO_KMS_ENCLAVE="object-store-pc2"
```