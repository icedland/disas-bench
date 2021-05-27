make-bench-cs:
	$(CC) main.c -flto -O3 -o bench-cs-fmt -I../../libs/capstone/include ../../libs/capstone/build/libcapstone.a

clean:
	rm -f bench-cs* *.o
