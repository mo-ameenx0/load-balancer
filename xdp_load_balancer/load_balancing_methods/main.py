import random
import subprocess
import json

BACKEND_A_IP = ['0xc0','0xa8','0x64','0x08']
BACKEND_A_MAC= ['0x52','0x54','0x00','0x7e','0x99','0xf2']

BACKEND_B_IP = ['0xc0','0xa8','0x64','0x06']
BACKEND_B_MAC= ['0x52','0x54','0x00','0x8b','0x69','0xfc']

BACKEND_C_IP = ['0xc0','0xa8','0x64','0x04']
BACKEND_C_MAC= ['0x52','0x54','0x00','0x49','0x43','0xe0']

B_FLAG = ['0x42']

def main():
    command = ['bpftool', 'map', 'update', 'name', 'xdp_lb_map', 'key', '0', '0', '0', '0', 'value']
    command.extend(BACKEND_A_MAC)
    command.extend(['0x00'])
    command.extend(['0x00'])
    command.extend(BACKEND_A_IP)
    subprocess.run(command)
    
    while True:
        rand = random.randint(0, 3)

        res = subprocess.run(['bpftool', 'map', 'dump', 'name', 'xdp_lb_map', '-j'], stdout=subprocess.PIPE)
        output = json.loads(res.stdout.decode('utf-8'))[0]
        value = output['value']

        flag = bytes.fromhex(value[6][2:]).decode('ascii')

        if flag == 'R':
            command = ['bpftool', 'map', 'update', 'name', 'xdp_lb_map', 'key', '0', '0', '0', '0', 'value']
            if rand == 0:
                command.extend(BACKEND_A_MAC)
                command.extend(['0x00'])
                command.extend(['0x00'])
                command.extend(BACKEND_A_IP)
            elif rand == 1:
                command.extend(BACKEND_B_MAC)
                command.extend(['0x00'])
                command.extend(['0x00'])
                command.extend(BACKEND_B_IP)
            else:
                command.extend(BACKEND_C_MAC)
                command.extend(['0x00'])
                command.extend(['0x00'])
                command.extend(BACKEND_C_IP)
            subprocess.run(command)


if __name__ == '__main__':    
    main()