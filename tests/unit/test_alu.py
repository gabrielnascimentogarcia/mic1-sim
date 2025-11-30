import unittest
from src.hardware.cpu.alu import ArithmeticLogicUnit
from src.common.constants import ALUOp, MASK_16BIT

class TestALU(unittest.TestCase):
    
    def setUp(self):
        self.alu = ArithmeticLogicUnit()

    def test_add_simple(self):
        """Teste básico de soma: 10 + 20 = 30"""
        res = self.alu.execute(ALUOp.ADD.value, 10, 20)
        self.assertEqual(res, 30)
        self.assertFalse(self.alu.Z) # Não deve ser zero
        self.assertFalse(self.alu.N) # Não deve ser negativo

    def test_add_overflow(self):
        """Teste de Overflow: 0xFFFF + 1 deve dar 0 (em 16 bits) e ativar flag Z"""
        # 65535 + 1 = 65536 -> 0x10000. Truncado para 16 bits -> 0x0000.
        res = self.alu.execute(ALUOp.ADD.value, 0xFFFF, 1)
        self.assertEqual(res, 0, "O overflow de 16 bits não funcionou corretamente.")
        self.assertTrue(self.alu.Z, "Flag Z deveria ser True para resultado 0.")
        self.assertFalse(self.alu.N, "Flag N não deveria ativar para 0.")

    def test_negative_flag(self):
        """Teste da Flag Negativo (bit mais significativo 1)"""
        # Se somarmos dois números positivos grandes, podemos ter um 'negativo' em complemento de 2
        # 0x7FFF (32767) + 1 = 0x8000 (-32768)
        res = self.alu.execute(ALUOp.ADD.value, 0x7FFF, 1)
        self.assertEqual(res, 0x8000)
        self.assertTrue(self.alu.N, "Flag N falhou. Bit 15 deveria indicar negativo.")
        self.assertFalse(self.alu.Z)

    def test_and_logic(self):
        """Teste da operação AND (bit a bit)"""
        # 0x00FF AND 0x0F0F -> 0x000F
        res = self.alu.execute(ALUOp.AND.value, 0x00FF, 0x0F0F)
        self.assertEqual(res, 0x000F)

    def test_identity_pass_through(self):
        """Teste de Identidade: Deve passar o valor de A inalterado"""
        # Usado para mover dados (ex: AC := AC)
        val = 0x1234
        res = self.alu.execute(ALUOp.IDENTITY.value, val, 0xFFFF) # B deve ser ignorado
        self.assertEqual(res, val)

    def test_not_inversion(self):
        """Teste de NOT (Inversão bit a bit)"""
        # NOT 0x0000 -> 0xFFFF
        res = self.alu.execute(ALUOp.NOT.value, 0x0000, 0)
        self.assertEqual(res, 0xFFFF)
        self.assertTrue(self.alu.N, "0xFFFF representa -1, então N deve ser True.")

if __name__ == '__main__':
    unittest.main()