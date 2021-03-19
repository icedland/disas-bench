#include "../load_bin.inc"
#include <udis86.h>

int main(int argc, char *argv[])
{
    uint8_t *code = NULL;
    size_t code_len = 0, loop_count = 0;
    if (!read_file(argc, argv, &code, &code_len, &loop_count))
    {
        return 1;
    }

    ud_t ud_obj;
    ud_init(&ud_obj);
    ud_set_mode(&ud_obj, 64);
#ifndef DISAS_BENCH_NO_FORMAT
    ud_set_syntax(&ud_obj, UD_SYN_INTEL);
#endif
    ud_set_vendor(&ud_obj, UD_VENDOR_ANY);

    clock_t start_time = clock();
    for (size_t round = 0; round < loop_count; ++round)
    {
        ud_set_input_buffer(&ud_obj, code, code_len);
        ud_set_pc(&ud_obj, 0);
        for (;;)
        {
            int len =
#ifdef DISAS_BENCH_NO_FORMAT
                ud_decode(&ud_obj);
#else
                ud_disassemble(&ud_obj);
#endif
            if (len <= 0)
                break;
        }
    }
    clock_t end_time = clock();

    printf(
        "%.2f ms\n",
        (double)(end_time - start_time) * 1000.0 / CLOCKS_PER_SEC);

    return 0;
}
