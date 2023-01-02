from vm_manager import VMsManager, VMEntry
from ebpf_map import eBPFMap
from methods import Methods

import random
import time

def main():
    number_of_min = 1
    start_time = time.time()

    xdp_lb_map = eBPFMap('xdp_lb_map')
    vms_manager = VMsManager()
    methods = Methods(vms_manager)

    init_vm: VMEntry = vms_manager.vms_entries[0]

    ext = []
    ext.extend(init_vm.vm_mac_hex)
    ext.extend(['00']) # Reset/Write the is_read flag
    ext.extend(['00']) # Add the last byte in the first block
    ext.extend(init_vm.vm_ip_hex)
    xdp_lb_map.write_map(ext)


    while True:
        flag = xdp_lb_map.get_ready_flag()

        if flag == 'R':

            ext = methods.random()

            xdp_lb_map.write_map(ext)

        if (time.time() - start_time) >= (number_of_min * 30):
            print(f'Number of Passed Minutes = {number_of_min}')
            print(f"Number of Packets Recieved in a Minute = {methods.num_of_packets}")
            print(f"Number of Running VMS = {len(vms_manager.vms_entries)}")

            if methods.num_of_packets >= methods.MAX_NUM_PACKETS_PER_MIN:
                vms_manager.create_vm()
            else:
                vms_manager.delete_vm()
            
            number_of_min += 1
            methods.num_of_packets = 0

if __name__ == '__main__':
    main()
