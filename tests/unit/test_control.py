import unittest
from src.hardware.cpu.control import ControlUnit

class TestControlUnit(unittest.TestCase):
    
    def setUp(self):
        """Cria uma nova Unidade de Controle antes de cada teste."""
        self.cu = ControlUnit()

    def test_decode_complex_instruction(self):
        """
        Teste 'Cirúrgico':
        Constrói manualmente um inteiro de 32 bits com valores conhecidos em cada campo,
        e verifica se o método .decode() extrai cada valor perfeitamente.
        
        Layout dos Bits (Baseado no PDF):
        [AMUX(1)|COND(2)|ALU(2)|SH(2)|MBR(1)|MAR(1)|RD(1)|WR(1)|ENC(1)|C(4)|B(4)|A(4)|ADDR(8)]
        """
        
        # --- Cenário de Teste (Valores Arbitrários para validação) ---
        # AMUX = 1 (Usar MBR)
        # COND = 2 (Jump se Zero - 10 bin)
        # ALU  = 3 (NOT - 11 bin)
        # SH   = 1 (Right Shift - 01 bin)
        # MBR=1, MAR=0, RD=1, WR=0, ENC=1
        # C=5 (0101), B=2 (0010), A=8 (1000)
        # ADDR = 255 (0xFF)

        # Construção manual do bitfield (esperado)
        # Bit 31 (AMUX) até Bit 0 (ADDR)
        microinstruction_bits = (
            (1 << 31) |  # AMUX
            (2 << 29) |  # COND
            (3 << 27) |  # ALU
            (1 << 25) |  # SH
            (1 << 24) |  # MBR
            (0 << 23) |  # MAR
            (1 << 22) |  # RD
            (0 << 21) |  # WR
            (1 << 20) |  # ENC
            (5 << 16) |  # C
            (2 << 12) |  # B
            (8 << 8)  |  # A
            (255 << 0)   # ADDR
        )

        # Injeta diretamente no MIR (pulando o fetch para testar isoladamente o decode)
        self.cu.MIR = microinstruction_bits
        
        # Executa a decodificação
        signals = self.cu.decode()

        # --- Asserções (Validação) ---
        self.assertEqual(signals.amux, 1, "Erro no campo AMUX")
        self.assertEqual(signals.cond, 2, "Erro no campo COND")
        self.assertEqual(signals.alu, 3,  "Erro no campo ALU")
        self.assertEqual(signals.sh, 1,   "Erro no campo SH")
        
        self.assertTrue(signals.mbr,  "Erro no sinal MBR")
        self.assertFalse(signals.mar, "Erro no sinal MAR")
        self.assertTrue(signals.rd,   "Erro no sinal RD")
        self.assertFalse(signals.wr,  "Erro no sinal WR")
        self.assertTrue(signals.enc,  "Erro no sinal ENC")
        
        self.assertEqual(signals.c, 5, "Erro no campo C")
        self.assertEqual(signals.b, 2, "Erro no campo B")
        self.assertEqual(signals.a, 8, "Erro no campo A")
        self.assertEqual(signals.addr, 255, "Erro no campo ADDR")

    def test_fetch_logic(self):
        """Verifica se o FETCH busca a instrução correta da memória baseada no MPC."""
        # Coloca uma 'instrução mágica' no endereço 10 da memória de controle
        magic_instruction = 0xCAFEBABE
        self.cu.control_store[10] = magic_instruction
        
        # Aponta o MPC para 10
        self.cu.update_mpc(10)
        
        # Executa o Fetch
        self.cu.fetch()
        
        # Verifica se o MIR recebeu o valor
        self.assertEqual(self.cu.MIR, magic_instruction, "O MIR não foi atualizado corretamente pelo FETCH.")

if __name__ == '__main__':
    unittest.main()