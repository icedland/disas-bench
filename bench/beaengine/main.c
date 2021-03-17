#include "../load_bin.inc"
#include <beaengine/BeaEngine.h>

int main(int argc, char *argv[])
{
    uint8_t *code = NULL;
    size_t code_len = 0, loop_count = 0;
    if (!read_file(argc, argv, &code, &code_len, &loop_count))
    {
        return 1;
    }

    DISASM disasm = {0};
    disasm.Archi = 64;

    size_t num_valid_insns = 0;
    size_t num_bad_insns = 0;
    UIntPtr code_end = (UIntPtr)code + code_len;
    clock_t start_time = clock();
    for (size_t round = 0; round < loop_count; ++round)
    {
        disasm.EIP = (UIntPtr)code;
        disasm.VirtualAddr = 0;
        for (UIntPtr code_curr = (UIntPtr)code; code_curr < code_end;)
        {
            disasm.EIP = code_curr;
            disasm.SecurityBlock = (UInt32)(code_end - code_curr);
            int res = Disasm(&disasm);
            if (res < 0)
            {
                num_bad_insns++;
                code_curr++;
            }
            else
            {
                num_valid_insns++;
                code_curr += (UIntPtr)res;
            }
        }
    }
    clock_t end_time = clock();

    printf(
        "Disassembled %zu instructions (%zu valid, %zu bad), %.2f ms\n",
        num_valid_insns + num_bad_insns,
        num_valid_insns,
        num_bad_insns,
        (double)(end_time - start_time) * 1000.0 / CLOCKS_PER_SEC);

    return 0;
}
