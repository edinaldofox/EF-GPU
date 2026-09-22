# ALU8 — chip digital síncrono de 8 bits

`ef_gpu_alu8` é o primeiro design de referência do EF-GPU. É um bloco digital síncrono, não um chip fabricável isoladamente: a fabricação requer um PDK e etapas físicas ainda não configuradas.

## Interface

| Sinal | Direção | Descrição |
| --- | --- | --- |
| `clk` | entrada | Clock ativo na borda de subida. |
| `rst_n` | entrada | Reset síncrono ativo em nível baixo. |
| `en` | entrada | Quando alto, registra o resultado da ALU. |
| `op[2:0]` | entrada | Código de operação. |
| `a[7:0]`, `b[7:0]` | entrada | Operandos sem sinal, exceto na operação SLT. |
| `y[7:0]` | saída | Resultado registrado. |
| `zero`, `carry`, `overflow`, `error` | saída | Flags registradas do resultado. |

Com `en=0`, todas as saídas preservam seu estado. Com `rst_n=0`, as saídas são limpas na próxima borda de subida.

## Operações

| `op` | Nome | `y` | Flags especiais |
| --- | --- | --- | --- |
| `000` | ADD | `a + b` | `carry` é o bit 8; `overflow` é aritmético com sinal. |
| `001` | SUB | `a - b` | `carry=1` significa que não houve empréstimo; `overflow` é aritmético com sinal. |
| `010` | AND | `a & b` | — |
| `011` | OR | `a | b` | — |
| `100` | XOR | `a ^ b` | — |
| `101` | SLT | `1` se `signed(a) < signed(b)`, senão `0` | comparação com sinal. |
| `110` | PASS_A | `a` | — |
| `111` | Reservada | `0` | `error=1`. |

Em qualquer operação, `zero=1` quando `y` é zero.

## Evidência de validação esperada

- `formal/alu8_core_formal.sv` prova as equações do núcleo para todas as combinações de `a`, `b` e `op`.
- `tb/tb_ef_gpu_alu8.sv` cobre reset, retenção e operações registradas em um simulador SystemVerilog.
- `scripts/synth-alu8.sh` sintetiza o topo e apresenta estatísticas lógicas independentes de tecnologia.
- `configs/openroad/alu8/constraints.sdc` declara o clock de 10 ns. Não há resultado físico sem PDK.
