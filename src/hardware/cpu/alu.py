"""
Unidade Lógica e Aritmética (ULA/ALU) do MIC-1.
Realiza operações matemáticas e gera flags de estado (N, Z).
"""

from typing import Tuple
from src.common.constants import ALUOp, MASK_16BIT

class ArithmeticLogicUnit:
    def __init__(self):
        self.N = False  # Flag Negativo
        self.Z = False  # Flag Zero

    def execute(self, op: int, a: int, b: int) -> int:
        """
        Executa a operação (op) nos operandos A e B.
        Retorna o resultado de 16 bits e atualiza as flags internas N e Z.
        """
        result = 0

        # Mapeamento baseado no microprograma e diagrama
        if op == ALUOp.ADD.value:
            result = (a + b) & MASK_16BIT
        elif op == ALUOp.AND.value:
            result = a & b
        elif op == ALUOp.IDENTITY.value:
            result = a & MASK_16BIT  # Passa A direto (ignora B)
        elif op == ALUOp.NOT.value:
            result = (~a) & MASK_16BIT # Inverte bits de A (ignora B)
        else:
            # Caso de segurança (não deve acontecer com microcódigo correto)
            result = 0

        # Atualização das Flags (Baseado no resultado final)
        # Z: Verdadeiro se resultado for 0
        self.Z = (result == 0)
        
        # N: Verdadeiro se o bit mais significativo (bit 15) for 1
        self.N = bool((result >> 15) & 1)

        return result