make-bench-distorm:
	cc main.c -flto -O3 -o bench-distorm-fmt -I../../libs/distorm/include ../../libs/distorm/distorm3.a
	cc main.c -flto -O3 -o bench-distorm-no-fmt -DDISAS_BENCH_NO_FORMAT -I../../libs/distorm/include ../../libs/distorm/distorm3.a

clean:
	rm -f bench-distorm* *.o
