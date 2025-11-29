"""
Gerenciador de Memória (Memory Management Unit - MMU simplificada).
Coordena o acesso entre a CPU, a Cache (L1) e a Memória Principal (RAM).
Implementa a lógica de busca de blocos em caso de Cache Miss.
"""

from src.hardware.memory.ram import MainMemory
from src.hardware.memory.cache import DirectCache

class MemoryManager:
    def __init__(self, ram: MainMemory, cache: DirectCache):
        self.ram = ram
        self.cache = cache

    def read(self, address: int) -> int:
        """
        Lê uma palavra da memória (abstraindo a hierarquia).
        Fluxo:
        1. Consulta Cache.
        2. Se HIT: Retorna valor.
        3. Se MISS: 
           - Calcula endereço base do bloco.
           - Busca bloco inteiro na RAM.
           - Carrega bloco na Cache.
           - Retorna valor diretamente do bloco (sem gerar Hit falso).
        """
        # 1. Tenta ler da Cache
        value = self.cache.read(address)
        
        if value is not None:
            # Cache HIT
            return value

        # 2. Cache MISS - Precisamos buscar na RAM
        block_size = self.cache.block_size
        
        # Alinhamento: Se block_size=4 e address=6, start=4.
        block_start_address = address - (address % block_size)
        
        # Lê o bloco de palavras da RAM
        data_block = self.ram.read_block(block_start_address, block_size)
        
        # Carrega na Cache (substituindo a linha antiga)
        self.cache.load_block(block_start_address, data_block)
        
        # CORREÇÃO: Retorna o valor diretamente do bloco lido, 
        # sem chamar cache.read() novamente para não poluir as estatísticas de Hit.
        offset = address % block_size
        return data_block[offset]

    def write(self, address: int, value: int):
        """
        Escreve um valor na memória.
        Política: Write-Through (Escreve sempre na RAM) + Write-Update (Atualiza Cache se presente).
        """
        # 1. Escreve sempre na RAM (Memória persistente)
        self.ram.write(address, value)
        
        # 2. Tenta atualizar a Cache (se o bloco estiver carregado lá)
        self.cache.write_word(address, value)

    def get_stats(self):
        """Retorna estatísticas de desempenho da memória."""
        return self.cache.get_stats()