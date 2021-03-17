make-bench-udis86:
	cc main.c -o bench-udis86-fmt -O3 -I../../libs/udis86 ../../libs/udis86/libudis86/.libs/libudis86.a
	cc main.c -DDISAS_BENCH_NO_FORMAT -o bench-udis86-no-fmt -O3 -I../../libs/udis86 ../../libs/udis86/libudis86/.libs/libudis86.a

clean:
	rm -f bench-udis86* *.o
