make-bench-bddisasm:
	$(CC) main.c -flto -O3 -o bench-bddisasm-fmt -I../../libs/bddisasm/inc ../../libs/bddisasm/build/libbddisasm.a
	$(CC) main.c -flto -O3 -o bench-bddisasm-no-fmt -DDISAS_BENCH_NO_FORMAT -I../../libs/bddisasm/inc ../../libs/bddisasm/build/libbddisasm.a

clean:
	rm -f bench-bddisasm-fmt bench-bddisasm-no-fmt
