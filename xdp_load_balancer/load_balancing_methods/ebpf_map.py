import subprocess
import json

class eBPFMap():
    def __init__(self, map_name):
        self.map_name = map_name

    # The ready flag indicate that the xdp_load_balancer ready to send to new backend
    def get_ready_flag(self):
        res = subprocess.run(['bpftool', 'map', 'dump', 'name', self.map_name, '-j'], stdout=subprocess.PIPE)
        output = json.loads(res.stdout.decode('utf-8'))[0]
        value = output['value']

        flag = bytes.fromhex(value[6][2:]).decode('ascii')

        return flag

    def write_map(self, extension):
        command = []
        command = ['bpftool', 'map', 'update', 'name', self.map_name, 'key', '0', '0', '0', '0', 'value', 'hex']
        command.extend(extension)
        
        subprocess.run(command)
