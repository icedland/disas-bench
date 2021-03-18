make-bench-beaengine:
	cc main.c -flto -O3 -o bench-beaengine-fmt -DBEA_ENGINE_STATIC -I../../libs/beaengine/include ../../libs/beaengine/build/lib/$(shell uname -s).gnu.Release.64/libBeaEngine_s_l_64.a

clean:
	rm -f bench-beaengine* *.o
