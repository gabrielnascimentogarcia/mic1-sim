import unittest
from src.hardware.memory.ram import MainMemory
from src.hardware.memory.cache import DirectCache
from src.hardware.memory.manager import MemoryManager
from src.hardware.cpu.cpu import CPU

class TestFullProgram(unittest.TestCase):
    def setUp(self):
        self.mmu = MemoryManager(MainMemory(1024), DirectCache())
        self.cpu = CPU(self.mmu)

    def test_add_and_store(self):
        """
        Programa:
        0: LODD 100  (Carrega valor do endereço 100 no AC)
        1: ADDD 101  (Soma com valor do endereço 101)
        2: STOD 102  (Guarda resultado no endereço 102)
        3: JUMP 0    (Loop infinito - opcional, só pra testar o pulo)
        
        Dados:
        100: 15
        101: 25
        Esperado em 102: 40
        """
        # Compilação Manual (Opcode << 12 | Endereço)
        prog_0 = (0 << 12) | 100  # LODD 100
        prog_1 = (2 << 12) | 101  # ADDD 101
        prog_2 = (1 << 12) | 102  # STOD 102
        prog_3 = (6 << 12) | 0    # JUMP 0
        
        # Carrega Programa e Dados
        self.mmu.write(0, prog_0)
        self.mmu.write(1, prog_1)
        self.mmu.write(2, prog_2)
        self.mmu.write(3, prog_3)
        
        self.mmu.write(100, 15)
        self.mmu.write(101, 25)
        self.mmu.write(102, 0) # Limpa destino
        
        # Executa!
        # Cada instrução leva +- 6 a 10 microinstruções. 
        # Vamos rodar 50 ciclos para garantir.
        for _ in range(50):
            self.cpu.step()
            
        # Verifica resultado na Memória
        resultado = self.mmu.read(102)
        self.assertEqual(resultado, 40, f"Erro! Esperava 40 (15+25), mas encontrou {resultado}")

if __name__ == '__main__':
    unittest.main()