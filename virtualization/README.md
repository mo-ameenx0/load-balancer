# Kernel Based Virtualization (KVM)
KVM will be used as the virtualization side for the load-balancer. A template virtual machine with all the required tools to test the load-balancer will be created. Then the load-balancer will use the template virtual machine to clone/create new virtual machines as needed. The template virtual machine will have a simple nginx server setuped to send back some information related to the virtual machine. [Fedora 37: Netinstall ISO](https://download.fedoraproject.org/pub/fedora/linux/releases/37/Server/x86_64/iso/Fedora-Server-netinst-x86_64-37-1.7.iso) will be used to create the template.

## Setup
### Create Backend Template Virtual Machine
1. Create a folder to store the iso file.
    ```
    mkdir /var/lib/libvirt/isos
    ```
2. Download [Fedora 37: Netinstall ISO](https://download.fedoraproject.org/pub/fedora/linux/releases/37/Server/x86_64/iso/Fedora-Server-netinst-x86_64-37-1.7.iso).
    ```
    wget -P /var/lib/libvirt/isos \
    https://download.fedoraproject.org/pub/fedora/linux/releases/37/Server/x86_64/iso/Fedora-Server-netinst-x86_64-37-1.7.iso
    ```
3. Create the fedora virtual machine template. Follow the wizard to complete installation.
    ```
    virt-install \
    --name backend-template \
    --vcpus 2 \
    --ram 2048 \
    --console pty,target_type=serial \
    --cdrom /var/lib/libvirt/isos/Fedora-Server-netinst-x86_64-37-1.7.iso \
    --disk path=/var/lib/libvirt/images/backend-template.qcow2,size=10
    ```
4. Install general dependencies and setup the virtual machine.
    ```
    dnf update && dnf upgrade
    dnf group install "C Development Tools and Libraries" "Development Tools"
    dnf install hg ninja-build git cmake golang libunwind-devel pcre-devel
    ```
5. Clone boringssl and build it.
   ```
   git clone https://github.com/google/boringssl.git
   cd boringssl
   mkdir build
   cd build
   cmake -GNinja ..
   ninja
   ```
6. Clone nginx and build it with `http3` configurations.
   ```
   hg clone -b quic https://hg.nginx.org/nginx-quic
   cd nginx-quic
   ./auto/configure --with-debug --with-http_v3_module         \
                    --with-cc-opt="-I../boringssl/include"     \
                    --with-ld-opt="-L../boringssl/build/ssl    \
                                    -L../boringssl/build/crypto"
   make
   make install
   firewall-cmd --add-port=443/udp
   ./usr/local/nginx/sbin/nginx

   ```
7. Create OpenSSL certificate and key following the [tutorial](https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-on-centos-7)
8. Add the following config to nginx configurations under `/usr/local/nginx/conf/nginx.conf`.
    ```
    worker_processes 1;
    events {
        worker_connections 1024;
    }

    http {
        include     mime.types;
        default_type text/plain;

        sendfile on;
        keepalive_timeout 65;

        server {
            listen 443 ssl;              # TCP listener for HTTP/1.1
            listen 443 http3 reuseport;  # UDP listener for QUIC+HTTP/3

            ssl_protocols       TLSv1.3; # QUIC requires TLS 1.3
            ssl_certificate     /etc/ssl/certs/nginx.crt;
            ssl_certificate_key /etc/ssl/private/nginx.key;

            add_header Alt-Svc 'h3=":443"';   # Advertise that HTTP/3 is available
            add_header QUIC-Status $quic;     # Sent when QUIC was used

            location / {
                expires -1;
                return 200 'Server Address: $server_addr:$server_port\n';
            }
        }
    }
    ```
9.  Setup the client machine and install and configure curl for http3 following the [tutorial](https://curl.se/docs/http3.html#quiche-version)

**Now** the virtual machine template is ready we can clone the vm as needed by the load balancer. 


**Clone the template vm**
```
virt-clone \
  --original backend-template \
  --name cloned-vm \
  --file /var/lib/libvirt/images/cu.qcow2
```

## KVM Dependencies
To install KVM dependencies and required tools follow the following [tutorial](https://ubuntu.com/blog/kvm-hyphervisor)