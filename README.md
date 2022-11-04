# Introduction
Implement a load balancer that manages multiple virtual machines and expand or downsize the number of machines based on the network traffic. 
So, a network application will be deployed upon the load balancer which would read every packet sent to the network application and decide based on multiple algorithms (e.g., round robin) which virtual machine should response to the request.
Moreover, if there is a high load multiple virtual machines would be spawn on to deal with the high traffic. On the other hand, during low load the balancer will remove unnecessary virtual machines to cut down cost

# Development Tools
The idea is to use [eBPF](https://ebpf.io/) to intercept TCP packets and redirect the packet to virtual machines that are running using [KVM](https://www.linux-kvm.org/page/Main_Page)
**NOTE: The repository was developed using Ubuntu 22.04.1**

# Setup Dependencies
## 2. KVM Requirements

## 3. Monitoring Application (UI) Requirements
