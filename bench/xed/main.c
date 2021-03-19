#include "../load_bin.inc"
#include <xed-interface.h>


int main(int argc, char* argv[]) 
{
    xed_tables_init();

    uint8_t *code = NULL;
    size_t code_len = 0, loop_count = 0;
    if (!read_file(argc, argv, &code, &code_len, &loop_count))
    {
        return 1;
    }

    clock_t start_time = clock();
    for (size_t round = 0; round < loop_count; ++round)
    {
        for (size_t read_offs = 0; read_offs < code_len; )
        {
            xed_decoded_inst_t insn;
            xed_decoded_inst_zero(&insn);
            xed_decoded_inst_set_mode(
                &insn, 
                XED_MACHINE_MODE_LONG_64, 
                XED_ADDRESS_WIDTH_64b
            );
            
            xed_decode(
                &insn, 
                XED_STATIC_CAST(const xed_uint8_t*, code + read_offs),
                code_len - read_offs
            );
#ifndef DISAS_BENCH_NO_FORMAT
            char print_buf[256];
            xed_format_context(
                XED_SYNTAX_INTEL,
                &insn,
                print_buf,
                sizeof print_buf,
                0,
                NULL,
                NULL
            );
#endif
            read_offs += xed_decoded_inst_get_length(&insn);
        }
    }
    clock_t end_time = clock();

    printf(
        "%.2f ms\n", 
        (double)(end_time - start_time) * 1000.0 / CLOCKS_PER_SEC
    );
    
    return 0;
}
