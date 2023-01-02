import threading
import subprocess
import libvirt
import random
import string
import time
import re

conn = libvirt.openReadOnly(None)

class VMsThread(threading.Thread):
    def __init__(self, vms_manager, is_load_vm=True, vm_name=None):
        super().__init__()

        self.vms_manager = vms_manager

        self.is_load_vm = is_load_vm
        self.vm_name = vm_name

    def run(self):
        # load new vm
        if self.is_load_vm:
            letters = string.ascii_lowercase
            vm_name = ''.join(random.choice(letters) for i in range(8))

            print(f"Creating new vm with name {vm_name}")

            subprocess.run(['virt-clone', '--original', 'backend-template', '--name', vm_name, '--file', f'/var/lib/libvirt/images/{vm_name}.qcow2'])

            subprocess.run(['virsh', 'start', vm_name])

            time.sleep(30)

            for domain in conn.listAllDomains():
                if domain.name() == vm_name:
                    self.vms_manager.load_vm(domain)
                    break
        # delete vm
        else:
            subprocess.run(['virsh', 'destroy', self.vm_name])

            subprocess.run(['virsh', 'undefine', self.vm_name])

            subprocess.run(['rm', '-rf', f'/var/lib/libvirt/images/{self.vm_name}.qcow2'])

            print(f"{self.vm_name} has been deleted")

class VMsManager():
    MAX_VMS = 5
    MIN_VMS = 2
    def __init__(self):
        self.vms_entries = []

        self.load_vms()

    def load_vms(self):
        domains = conn.listAllDomains()
        for domain in domains:
            self.load_vm(domain)

    def load_vm(self, domain):
        if domain.isActive():
            if domain.name() != 'client' and domain.name() != 'backend-template':
                vm_entry = VMEntry(domain)
                
                print("Loaded new vm:")
                print(f"vm name = {vm_entry.vm_name}")
                print(f"vm ip = {vm_entry.vm_ip}")
                print(f"vm mac = {vm_entry.vm_mac}")
                print()

                self.vms_entries.append(vm_entry)

    def create_vm(self):
        if len(self.vms_entries) == self.MAX_VMS:
            print("Reached MAX Number of vms use admin need method to modify it")
            return
        VMsThread(self).start()    

    def delete_vm(self):
        if len(self.vms_entries) == self.MIN_VMS:
            print("Reached MIN Number of vms used admin need method to modify it")
            return

        vm_entry = self.vms_entries[-1]
        VMsThread(self, is_load_vm=False, vm_name=vm_entry.vm_name).start()
        self.vms_entries.pop()

class VMEntry():
    def __init__(self, domain):
        self.domain = domain
        self.vm_name = domain.name()
        
        self.vm_ip = None
        self.vm_ip_hex = None

        self.vm_mac = None
        self.vm_mac_hex = None

        self.load_network_info()

    def load_network_info(self):
        self.vm_mac = re.search(r"<mac address='([a-zA-z0-9:]+)'", self.domain.XMLDesc(0)).group(1)

        process = subprocess.Popen(['/sbin/arp', '-a'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        process.wait()  # Wait for it to finish with the command
        for line in process.stdout:
            line = line.decode('utf-8')

            if self.vm_mac in str(line):
                self.vm_ip = re.search(r'(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})', line).group(1)

        # Convert the network info to hex so it can be used by ebpf
        self.vm_mac_hex = self.vm_mac.split(':')
        self.vm_ip_hex = [hex(int(value))[2:] for value in self.vm_ip.split('.')]

    def get_vm_usage(self):
        return random.randrange(0, 20)
