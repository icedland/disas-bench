xedpath=../../libs/intelxed

make-bench-xed:
	$(CC) main.c -flto -O3 -o bench-xed-fmt -I${xedpath}/include/public/xed -I${xedpath}/obj ${xedpath}/obj/libxed.a
	$(CC) main.c -flto -O3 -o bench-xed-no-fmt -DDISAS_BENCH_NO_FORMAT -I${xedpath}/include/public/xed -I${xedpath}/obj ${xedpath}/obj/libxed.a

clean:
	rm -f bench-xed* *.o
