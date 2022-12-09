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
4. Setup ngnix to send back the virtual machine information (Run the following commands in the virutal machine).
    ```
    dnf update
    dnf install nginx
    systemctl enable nginx
    systemctl start nginx
    firewall-cmd --permanent --add-service=http
    firewall-cmd --reload
    ```
5. Add the following config to nginx configurations under `/etc/nginx/conf.d/plain-text.conf`.
    ```
    server {
        listen 80;
        listen [::]:80;

        location / {
            default_type text/plain;
            expires -1;
            return 200 'Server address: $server_addr:$server_port\nDate: $time_local\nRequest ID: $request_id\n';
        }
    }
    ```
6. Check if the nginx server is started or not.
    ```
    systemctl status nginx
    ```
7. Access the nginx server from the host OS browser.
    ```
    http://VIRTUAL_MACHINE_IP:80
    ```

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