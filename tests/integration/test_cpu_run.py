import unittest
from src.hardware.memory.ram import MainMemory
from src.hardware.memory.cache import DirectCache
from src.hardware.memory.manager import MemoryManager
from src.hardware.cpu.cpu import CPU

class TestCPURun(unittest.TestCase):
    def setUp(self):
        # Setup do Sistema Completo
        self.ram = MainMemory(size=1024)
        self.cache = DirectCache()
        self.mmu = MemoryManager(self.ram, self.cache)
        self.cpu = CPU(self.mmu)

    def test_lodd_instruction(self):
        """
        Teste de Integração: Executa a instrução LODD (Load Direct).
        Programa:
           Endereço 0: LODD 50  (Binário: 0000 0000 0011 0010 -> 0x0032)
           Endereço 50: 999     (O valor que queremos carregar)
        """
        # 1. Carrega o programa na memória
        # Opcode LODD (0000) + Endereço 50 (000000110010) = 0x0032
        instruction_lodd = 0x0032 
        data_value = 999
        
        self.mmu.write(0, instruction_lodd) # Programa no endereço 0
        self.mmu.write(50, data_value)      # Dado no endereço 50

        # 2. Executa ciclos suficientes para completar Fetch + LODD
        # Fetch (3 passos: 0, 1, 2) + LODD (3 passos: 10, 11, 12) = 6 ciclos
        for _ in range(6):
            self.cpu.step()

        # 3. Verifica se o AC agora contém 999
        self.assertEqual(self.cpu.registers.AC, data_value, 
            f"O AC deveria ter carregado o valor {data_value} da memória.")

if __name__ == '__main__':
    unittest.main()