make-bench-beaengine:
	cc main.c -o bench-beaengine-fmt -O3 -DBEA_ENGINE_STATIC -I../../libs/beaengine/include ../../libs/beaengine/lib/$(shell uname -s).gnu.Release.64/libBeaEngine_s_l_64.a

clean:
	rm -f bench-beaengine* *.o
