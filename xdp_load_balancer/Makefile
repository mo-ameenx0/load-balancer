INTERFACE_DEVICE = virbr1

TARGET = xdp_load_balancer

BPF_C = ${TARGET:=.c}
BPF_OBJ = ${BPF_C:.c=.o}

xdp: $(BPF_OBJ)
	bpftool net detach xdpgeneric dev $(INTERFACE_DEVICE)
	rm -f /sys/fs/bpf/$(TARGET)
	bpftool prog load $(BPF_OBJ) /sys/fs/bpf/$(TARGET)
	bpftool net attach xdpgeneric pinned /sys/fs/bpf/$(TARGET) dev $(INTERFACE_DEVICE) 

$(BPF_OBJ): %.o: %.c
	clang -S \
	    -target bpf \
	    -D __BPF_TRACING__ \
	    -Ilibbpf/src\
	    -Wall \
	    -Wno-unused-value \
	    -Wno-pointer-sign \
	    -Wno-compare-distinct-pointer-types \
	    -Werror \
	    -O2 -emit-llvm -c -o ${@:.o=.ll} $<
	llc -march=bpf -filetype=obj -o $@ ${@:.o=.ll}

clean:
	bpftool net detach xdpgeneric dev $(INTERFACE_DEVICE)
	rm -f /sys/fs/bpf/$(TARGET)
	rm $(BPF_OBJ)
	rm ${BPF_OBJ:.o=.ll}
