#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

SEC("xdp_drop_all")
int xdp_drop_all_prog(struct xdp_md *ctx)
{
    return XDP_DROP;
}

char _licence[] SEC("licence") = "GPL";