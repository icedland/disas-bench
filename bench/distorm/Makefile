make-bench-distorm:
	cc main.c -o bench-distorm-fmt -O3 -I../../libs/distorm/include ../../libs/distorm/distorm3.a
	cc main.c -DDISAS_BENCH_NO_FORMAT -o bench-distorm-no-fmt -O3 -I../../libs/distorm/include ../../libs/distorm/distorm3.a

clean:
	rm -f bench-distorm* *.o
