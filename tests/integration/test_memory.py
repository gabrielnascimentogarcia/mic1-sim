import unittest
from src.hardware.memory.ram import MainMemory
from src.hardware.memory.cache import DirectCache
from src.hardware.memory.manager import MemoryManager

class TestMemorySystem(unittest.TestCase):
    
    def setUp(self):
        # RAM de 1024 palavras
        self.ram = MainMemory(size=1024)
        # Cache: 16 linhas, Blocos de 4 palavras
        self.cache = DirectCache(size_lines=16, block_size=4)
        # Gerenciador
        self.mmu = MemoryManager(self.ram, self.cache)

    def test_spatial_locality(self):
        """
        Prova que ler o endereço X traz os vizinhos (X+1) para a cache (Bloco).
        """
        # 1. Setup: Popula a RAM nos endereços 16, 17, 18, 19 (Bloco alinhado)
        self.ram.write(16, 0xAAAA)
        self.ram.write(17, 0xBBBB)
        self.ram.write(18, 0xCCCC)
        self.ram.write(19, 0xDDDD)

        # 2. Leitura do primeiro endereço (Cold Miss)
        val1 = self.mmu.read(16)
        self.assertEqual(val1, 0xAAAA)
        
        stats = self.mmu.get_stats()
        self.assertEqual(stats['misses'], 1, "A primeira leitura deveria ser Miss.")
        self.assertEqual(stats['hits'], 0)

        # 3. Leitura do segundo endereço (Vizinho)
        # Se a cache de blocos funcionar, o 17 já deve estar lá!
        val2 = self.mmu.read(17)
        self.assertEqual(val2, 0xBBBB)
        
        stats = self.mmu.get_stats()
        self.assertEqual(stats['misses'], 1, "Ainda deve ter apenas 1 Miss.")
        self.assertEqual(stats['hits'], 1, "A leitura do vizinho (17) deveria ser Hit (Localidade Espacial).")

    def test_write_through_policy(self):
        """
        Verifica se a escrita vai para a RAM e atualiza a Cache se houver Hit.
        """
        # Carrega o bloco 0-3 na cache (Lendo endereço 0)
        self.mmu.read(0) 
        
        # Agora escreve no endereço 1 (que está na cache)
        self.mmu.write(1, 0x9999)
        
        # Verifica RAM (Write-Through)
        self.assertEqual(self.ram.read(1), 0x9999, "RAM deve ser atualizada.")
        
        # Verifica Cache (Write-Update)
        # Lendo da cache diretamente para garantir que ela foi atualizada internamente
        # (simulando acesso rápido posterior)
        cache_val = self.cache.read(1)
        self.assertEqual(cache_val, 0x9999, "Cache deve ser atualizada no Write Hit.")

    def test_block_alignment(self):
        """
        Verifica se o sistema calcula o início do bloco corretamente.
        Se eu pedir o endereço 6 (bloco de 4), ele deve carregar 4, 5, 6, 7.
        """
        self.ram.write(4, 100)
        self.ram.write(5, 101)
        self.ram.write(6, 102)
        self.ram.write(7, 103)
        
        # Pede endereço 6 (meio do bloco)
        val = self.mmu.read(6)
        self.assertEqual(val, 102)
        
        # Agora pede endereço 4 (início do bloco) -> Deve ser HIT
        val_start = self.mmu.read(4)
        stats = self.mmu.get_stats()
        
        self.assertEqual(stats['hits'], 1, "O endereço 4 deveria ter vindo junto com o 6.")

if __name__ == '__main__':
    unittest.main()