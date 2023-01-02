from vm_manager import VMsManager, VMEntry

import random

class Methods():
    MAX_NUM_PACKETS_PER_MIN = 500
    def __init__(self, vm_manager):
        self.vms_manager: VMsManager = vm_manager

        self.num_of_packets = 0

    def random(self):
        rand = random.randint(0, len(self.vms_manager.vms_entries) - 1)

        vm_entry: VMEntry = self.vms_manager.vms_entries[rand]

        # print('RANDOM METHOD')
        # print(f'Sending to {vm_entry.vm_name}')

        ext = []
        ext.extend(vm_entry.vm_mac_hex)
        ext.extend(['00'])
        ext.extend(['00'])
        ext.extend(vm_entry.vm_ip_hex)

        self.num_of_packets += 1

        return ext

    round_robin_index = 0
    def round_robin(self):
        if self.round_robin_index == len(self.vms_manager.vms_entries):
            self.round_robin_index = 0
        
        vm_entry: VMEntry = self.vms_manager.vms_entries[self.round_robin_index]
        self.round_robin_index += 1
        
        # print('ROUND ROBIN METHOD')
        # print(f'Sending to {vm_entry.vm_name}')

        ext = []
        ext.extend(vm_entry.vm_mac_hex)
        ext.extend(['00'])
        ext.extend(['00'])
        ext.extend(vm_entry.vm_ip_hex)

        self.num_of_packets += 1

        return ext

    def vm_usage(self):
        vm_lowest_usage_index = 0
        vm_lowest_usage = self.vms_manager.vms_entries[vm_lowest_usage_index].get_vm_usage()

        for i, vm in enumerate(self.vms_manager.vms_entries):
            temp = vm.get_vm_usage()
            if temp < vm_lowest_usage:
                vm_lowest_usage = temp
                vm_lowest_usage_index = i

        vm_entry: VMEntry = self.vms_manager.vms_entries[vm_lowest_usage_index]

        # print('VM USAGE METHOD')
        # print(f'Sending to the lowest usage VM {vm_entry.vm_name}')

        ext = []
        ext.extend(vm_entry.vm_mac_hex)
        ext.extend(['00'])
        ext.extend(['00'])
        ext.extend(vm_entry.vm_ip_hex)

        self.num_of_packets += 1

        return ext

    def admin_needs(self, MIN_VMS, MAX_VMS, MAX_NUM_PACKETS_PER_MIN):
        self.MAX_NUM_PACKETS_PER_MIN = MAX_NUM_PACKETS_PER_MIN
        self.vms_manager.MIN_VMS = MIN_VMS
        self.vms_manager.MAX_VMS = MAX_VMS

        self.vm_usage()
        
        self.num_of_packets += 1
