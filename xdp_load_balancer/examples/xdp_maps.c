#include <stddef.h>
#include <linux/bpf.h>
#include <linux/in.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_endian.h>

struct tcprec {
	__u64 rx_tcp_packets;
};

struct bpf_map_def SEC("maps") xdp_tcp_map = {
	.type        = BPF_MAP_TYPE_ARRAY,
	.key_size    = sizeof(__u32),
	.value_size  = sizeof(struct tcprec),
	.max_entries = 1,
};

SEC("xdp_count_tcp")
int xdp_count_tcp_prog(struct xdp_md *ctx)
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

    bpf_printk("Got TCP packet from %x", iph->daddr);

	/* Lookup in kernel BPF-side return pointer to actual data record */
    __u32 key = 0;
	struct tcprec *rec = bpf_map_lookup_elem(&xdp_tcp_map, &key);
    
	if (!rec){
        bpf_printk("Failed to read the map");
        return XDP_PASS;
    }
    
	rec->rx_tcp_packets++;

    bpf_printk("Read value = %d", rec->rx_tcp_packets);

    return XDP_PASS;
}

char _license[] SEC("license") = "GPL";