"""
Cache com Mapeamento Direto e Suporte a Blocos.
Implementa a lógica de Tag, Index e Offset.
"""

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class CacheLine:
    valid: bool = False
    tag: int = 0
    # Agora 'data' é uma lista de palavras (o bloco), não apenas um inteiro.
    data: List[int] = field(default_factory=lambda: [0, 0, 0, 0])

class DirectCache:
    def __init__(self, size_lines: int = 16, block_size: int = 4):
        """
        Inicializa a cache.
        :param size_lines: Número de linhas (slots). Padrão didático: 16.
        :param block_size: Palavras por linha. Padrão didático: 4.
        """
        self.size_lines = size_lines
        self.block_size = block_size
        self.lines: List[CacheLine] = [CacheLine(data=[0]*block_size) for _ in range(size_lines)]
        
        self.hits = 0
        self.misses = 0

    def _decode_address(self, address: int):
        """
        Quebra o endereço em Tag, Index e Offset.
        Considerando Block=4 (2 bits) e Lines=16 (4 bits).
        """
        # Offset: Bits menos significativos (log2(block_size))
        # Para size 4, são 2 bits (mask 0x3)
        offset = address & (self.block_size - 1)
        
        # Index: Bits do meio (log2(size_lines))
        # Shiftamos o offset para descartá-lo, depois aplicamos a máscara
        address_shifted = address >> 2  # Desloca 2 bits (offset)
        index = address_shifted & (self.size_lines - 1) # Mask 0xF para 16 linhas
        
        # Tag: Bits restantes
        # Shiftamos offset (2) + index (4) = 6 bits
        tag = address >> 6
        
        return tag, index, offset

    def read(self, address: int) -> Optional[int]:
        """
        Tenta ler da cache.
        Retorna o valor (int) se for HIT.
        Retorna None se for MISS.
        """
        tag, index, offset = self._decode_address(address)
        line = self.lines[index]

        # Verifica HIT: Bit de validade está ativo E a Tag bate?
        if line.valid and line.tag == tag:
            self.hits += 1
            return line.data[offset] # Retorna apenas a palavra solicitada do bloco
        
        # MISS
        self.misses += 1
        return None

    def load_block(self, address: int, data_block: List[int]):
        """
        Carrega um bloco inteiro vindo da RAM para a Cache (após um Miss).
        'address' deve ser o endereço base do bloco.
        """
        if len(data_block) != self.block_size:
            raise ValueError(f"Tamanho do bloco incorreto. Esperado {self.block_size}, recebeu {len(data_block)}.")

        tag, index, _ = self._decode_address(address)
        
        # Substitui a linha inteira
        self.lines[index] = CacheLine(valid=True, tag=tag, data=data_block)

    def write_word(self, address: int, value: int) -> bool:
        """
        Tenta escrever na cache (apenas se já estiver carregada -> Write Hit).
        Retorna True se foi Hit (atualizou), False se foi Miss (ignora).
        """
        tag, index, offset = self._decode_address(address)
        line = self.lines[index]

        if line.valid and line.tag == tag:
            # HIT: Atualiza apenas a palavra específica dentro do bloco
            line.data[offset] = value
            # (Em um sistema real, marcaríamos 'dirty bit' aqui se fosse Write-Back)
            return True
        
        return False # MISS: Não faz nada na cache (Write-No-Allocate simples)

    def get_stats(self) -> dict:
        return {"hits": self.hits, "misses": self.misses}
    
    def reset_stats(self):
        self.hits = 0
        self.misses = 0