#include "xdp_load_balancer.h"

#define IP_ADDRESS(x) (unsigned int)(192 + (168 << 8) + (100 << 16) + (x << 24))
#define CLIENT 2
#define LB 1

// Every map block is of size 8
struct flags {
    unsigned char vm_mac[6];    //size 6 bytes
    unsigned char is_ready;     //size 1 byte
	__be32 vm_ip;               //size 4 bytes
};

struct bpf_map_def SEC("maps") xdp_lb_map = {
	.type        = BPF_MAP_TYPE_ARRAY,
	.key_size    = sizeof(__u32),
	.value_size  = sizeof(struct flags),
	.max_entries = 1,
};

SEC("xdp_lb")
int xdp_load_balancer(struct xdp_md *ctx)
{
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;

    bpf_printk("got something");

    // Handle data as an ethernet frame header
    struct ethhdr *eth = data;

    // Check frame size
    if (data + sizeof(struct ethhdr) > data_end)
        return XDP_ABORTED;

    // Check protocol only accept IP
    if (bpf_ntohs(eth->h_proto) != ETH_P_IP)
        return XDP_PASS;

    // Check packet size
    struct iphdr *iph = data + sizeof(struct ethhdr);
    if (data + sizeof(struct ethhdr) + sizeof(struct iphdr) > data_end)
        return XDP_ABORTED;

    // Check protocol only accept TCP
    if (iph->protocol != IPPROTO_TCP)
        return XDP_PASS;
    
    __u32 key = 0;
	struct flags *rec = bpf_map_lookup_elem(&xdp_lb_map, &key);
	if (!rec){
        bpf_printk("Failed to read the map");
        return XDP_PASS;
    }

    if (iph->saddr == IP_ADDRESS(CLIENT))
    {
        iph->daddr = rec->vm_ip;
        for (int i = 0; i < sizeof(eth->h_dest); i++){
            eth->h_dest[i] = rec->vm_mac[i];
            bpf_printk("%x", eth->h_dest[i]);
        }
        bpf_printk("Got TCP packet from %x", rec->vm_ip);

    }
    else
    {
        // The client is hardcoded
        bpf_printk("From Backend");
        iph->daddr = IP_ADDRESS(CLIENT);
        eth->h_dest[0] = 0x52;
        eth->h_dest[1] = 0x54;
        eth->h_dest[2] = 0x00;
        eth->h_dest[3] = 0xd0;
        eth->h_dest[4] = 0x3e;
        eth->h_dest[5] = 0xab;

        rec->is_ready = 'R';
    }
    // The load balancer interface is hardcoded
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