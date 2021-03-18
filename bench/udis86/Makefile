# Note that -flto has been disabled, see make-all.sh
make-bench-udis86:
	cc main.c -O3 -o bench-udis86-fmt -I../../libs/udis86 ../../libs/udis86/libudis86/.libs/libudis86.a
	cc main.c -O3 -o bench-udis86-no-fmt -DDISAS_BENCH_NO_FORMAT -I../../libs/udis86 ../../libs/udis86/libudis86/.libs/libudis86.a

clean:
	rm -f bench-udis86* *.o
