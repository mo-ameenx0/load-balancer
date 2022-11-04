# Introduction
Implement a load balancer that manages multiple virtual machines and expand or downsize the number of machines based on the network traffic. 
So, a network application will be deployed upon the load balancer which would read every packet sent to the network application and decide based on multiple algorithms (e.g., round robin) which virtual machine should response to the request.
Moreover, if there is a high load multiple virtual machines would be spawn on to deal with the high traffic. On the other hand, during low load the balancer will remove unnecessary virtual machines to cut down cost

**NOTE: The repository was developed using Ubuntu 22.04.1**

# Development Tools
The idea is to use [eBPF](https://ebpf.io/) to intercept TCP packets and redirect the packet to virtual machines that are running using [KVM](https://www.linux-kvm.org/page/Main_Page)

## 1. eBPF
All the scripts written for eBPF are under `xdp_load_balancer`
### 1.1. Examples
To run a simple example that would drop all incoming packets follow the steps:
1. Compile the program
```
./xdp_load_balancer/compile_xdp xdp_load_balancer/examples/xdp_drop_all.c
```
1. To investigate the built `xdp_drop_all.o` run the following commands

```
llvm-objdump -h xdp_load_balancer/examples/xdp_drop_all.o
```
*llvm-objdump -h will show all the sections in the elf file*

```
llvm-objdump -S xdp_load_balancer/examples/xdp_drop_all.o
```
*llvm-objdump -S will show the elf file disassembled object*

3. Load the xdp program
Loading the `example/xdp_drop_all.o` program to the default interface you will loss connection. So attach the program to test/virtual interface.

To attach the program there are multiple steps:
```
ip link set dev INTERFACE_NAME xdpgeneric obj xdp_load_balancer/examples/xdp_drop_all.o sec xdp_drop_all
```

```
bpftool prog load xdp_load_balancer/examples/xdp_drop_all.o /sys/fs/bpf/xdp_drop_all
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
bpftool net detach xdpgeneric dev INTERFACE_NAME
```

**Note loading xdp program using ip is incompatible when using maps**

### 1.2. Resources
* [XDP-Tutorial](https://github.com/xdp-project/xdp-tutorial)
* [Get started with XDP-Red Hat](https://developers.redhat.com/blog/2021/04/01/get-started-with-xdp)

# Setup Dependencies
This repo was developed using **`Ubuntu`**.

## 1. eBPF Dependencies
To install the eBPF dependencies follow the following [README](https://github.com/xdp-project/xdp-tutorial/blob/master/setup_dependencies.org)

## 2. KVM Requirements

## 3. Monitoring Application (UI) Requirements
