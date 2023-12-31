# eBPF
## Examples
## 1. Drop All Packets
To run a simple example that would drop all incoming packets follow the steps:
1. Compile the program
    ```
    clang -O2 -g -target bpf -c examples/xdp_drop_all.c -o examples/xdp_drop_all.o 
    ```
2. To investigate the built `xdp_drop_all.o` run the following commands
    ```
    llvm-objdump -h examples/xdp_drop_all.o
    ```
    *llvm-objdump -h will show all the sections in the elf file*

    ```
    llvm-objdump -S examples/xdp_drop_all.o
    ```
    *llvm-objdump -S will show the elf file disassembled object*

3. Load the xdp program
    Loading the `example/xdp_drop_all.o` program to the default interface you will loss connection. So attach the program to test/virtual interface.

    To attach the program there are multiple steps:
    ```
    ip link set dev INTERFACE_NAME xdpgeneric obj examples/xdp_drop_all.o sec xdp_drop_all
    ```

    ```
    bpftool prog load examples/xdp_drop_all.o /sys/fs/bpf/xdp_drop_all
    bpftool net attach xdpgeneric pinned /sys/fs/bpf/xdp_drop_all dev INTERFACE_NAME
    ```

4. To show the attached xdp program
    ```
    ip link list dev INTERFACE_NAME
    ```

    ```
    bpftool net list dev INTERFACE_NAME
    ```

5. Deattach attached xdp program
    ```
    ip link set dev INTERFACE_NAME xdpgeneric off
    ```

    ```
    rm -f /sys/fs/bpf/xdp_drop_all
    bpftool net detach xdpgeneric dev INTERFACE_NAME
    ```
**Note loading xdp program using ip is incompatible when using maps**
## 2. Print Packets
To print the packets that passes through a specific interface follow the steps:
1. Compile the program
    ```
    clang -O2 -g -target bpf -c examples/xdp_print_packets.c -o examples/xdp_print_packets.o 
    ```
2. Load the xdp program to the wanted interface
    ```
    ip link set dev INTERFACE_NAME xdpgeneric obj examples/xdp_print_packets.o sec xdp_print_packets
    ```
3. Print the packets to the terminal
    ```
    cat /sys/kernel/debug/tracing/trace_pipe
    ```
4. Datatch the xdp program
    ```
    ip link set dev INTERFACE_NAME xdpgeneric off
    ```
## 3. Maps Kernel/User Spaces
eBPF provide a map as a shared storage to pass data between the user space and the kernel space. This example will use `bpftool` to read from the kernel space the number of tcp packets based through an interface.
1. Compile the program.
    ```
    clang -O2 -g -target bpf -c examples/xdp_maps.c -o examples/xdp_maps.o 
    ```
2. Load the xdp program to the wanted interface
    ```
    ip link set dev INTERFACE_NAME xdpgeneric obj examples/xdp_maps.o sec xdp_count_tcp
    ```
3. Monitor the recieved tcp packets
    ```
    cat /sys/kernel/debug/tracing/trace_pipe
    ```
4. Find the xdp program map id by listing all the ebpf maps
    ```
    bpftool map -f show
    ```
5. Read the program map using `bpftool` to find the number of tcp packets passed through the interface.
    ```
    bpftool map dump id MAP_ID
    ```
6. Datatch the xdp program
    ```
    ip link set dev INTERFACE_NAME xdpgeneric off
    ```
## Resources
* [Load-Balancer-From-Scratch](https://github.com/lizrice/lb-from-scratch)
* [XDP-Tutorial](https://github.com/xdp-project/xdp-tutorial)
* [Get started with XDP-Red Hat](https://developers.redhat.com/blog/2021/04/01/get-started-with-xdp)
* [eBPF readthedocs](https://prototype-kernel.readthedocs.io/en/latest/bpf/index.html)


## eBPF Dependencies
To install the eBPF dependencies follow the following [README](https://github.com/xdp-project/xdp-tutorial/blob/master/setup_dependencies.org)

**Add libbpf-dev tools**
```
sudo apt install libbpf-dev
sudo apt install -y gcc-multilib
```
