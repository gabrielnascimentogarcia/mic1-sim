import unittest
from src.hardware.cpu.registers import Registers
from src.common.constants import MASK_16BIT

class TestRegisters(unittest.TestCase):
    
    def setUp(self):
        """Executado antes de cada teste: cria uma CPU 'limpa'."""
        self.regs = Registers()

    def test_initialization(self):
        """Auditoria: Todos os registradores devem iniciar zerados (Reset state)."""
        state = self.regs.debug_state()
        for name, value in state.items():
            self.assertEqual(value, 0, f"O registrador {name} deveria iniciar com 0.")

    def test_write_read_valid_value(self):
        """Teste de fluxo normal: Escrever e ler um valor de 16 bits válido."""
        val = 0x1234
        self.regs.write('AC', val)
        self.assertEqual(self.regs.read('AC'), val, "Falha ao ler/escrever valor válido no AC.")

    def test_overflow_clamping(self):
        """
        CRÍTICO: Simulação de barramento de 16 bits.
        Se escrevermos 0xABCDE (20 bits), o registrador deve guardar apenas 0xBCDE (16 bits).
        Isso valida a constante MASK_16BIT = 0xFFFF.
        """
        input_val = 0xABCDE         # 1010 1011 1100 1101 1110 (20 bits)
        expected_val = 0xBCDE       #      1011 1100 1101 1110 (16 bits inferiores)
        
        self.regs.write('SP', input_val)
        read_val = self.regs.read('SP')
        
        self.assertEqual(read_val, expected_val, 
            f"Erro de Truncamento! Escreveu {hex(input_val)}, esperava {hex(expected_val)}, leu {hex(read_val)}.")

    def test_max_value_boundary(self):
        """Teste de borda: Valor máximo permitido (0xFFFF)."""
        self.regs.write('MAR', 0xFFFF)
        self.assertEqual(self.regs.read('MAR'), 0xFFFF)

    def test_invalid_register_access(self):
        """Segurança: Tentar acessar registrador inexistente deve falhar."""
        with self.assertRaises(ValueError):
            self.regs.write('XYZ', 10)
        
        with self.assertRaises(ValueError):
            self.regs.read('XYZ')

if __name__ == '__main__':
    unittest.main()