#include "xdp_load_balancer.h"

#define IP_ADDRESS(x) (unsigned int)(192 + (168 << 8) + (100 << 16) + (x << 24))
#define BACKEND_A 4
#define CLIENT 6
#define LB 1

SEC("xdp_lb")
int xdp_load_balancer(struct xdp_md *ctx)
{
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;

    bpf_printk("got something");

    // Handle data as an ethernet frame header
    struct ethhdr *eth = data;

    // Check frame header size
    if (data + sizeof(struct ethhdr) > data_end)
        return XDP_ABORTED;

    // Check protocol
    if (bpf_ntohs(eth->h_proto) != ETH_P_IP)
        return XDP_PASS;

    // Check packet header size
    struct iphdr *iph = data + sizeof(struct ethhdr);
    if (data + sizeof(struct ethhdr) + sizeof(struct iphdr) > data_end)
        return XDP_ABORTED;

    // Check protocol
    if (iph->protocol != IPPROTO_TCP)
        return XDP_PASS;

    bpf_printk("Got TCP packet from %x", iph->daddr);

    if (iph->saddr == IP_ADDRESS(CLIENT))
    {
        bpf_printk("From Client");
        iph->daddr = IP_ADDRESS(BACKEND_A);
        eth->h_dest[0] = 0x52;
        eth->h_dest[1] = 0x54;
        eth->h_dest[2] = 0x00;
        eth->h_dest[3] = 0x63;
        eth->h_dest[4] = 0xc4;
        eth->h_dest[5] = 0x90;
    }
    else
    {
        bpf_printk("From Backend");
        iph->daddr = IP_ADDRESS(CLIENT);
        eth->h_dest[0] = 0x52;
        eth->h_dest[1] = 0x54;
        eth->h_dest[2] = 0x00;
        eth->h_dest[3] = 0xc1;
        eth->h_dest[4] = 0xeb;
        eth->h_dest[5] = 0x08;
    }
    iph->saddr = IP_ADDRESS(LB);
    eth->h_source[0] = 0x52;
    eth->h_source[1] = 0x54;
    eth->h_source[2] = 0x00;
    eth->h_source[3] = 0x46;
    eth->h_source[4] = 0x3e;
    eth->h_source[5] = 0x5a;

    iph->check = iph_csum(iph);

    return XDP_TX;
}

char _license[] SEC("license") = "GPL";