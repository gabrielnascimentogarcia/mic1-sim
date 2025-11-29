"""
Memória Principal (RAM) do MIC-1.
Armazena o programa e os dados.
Simula a latência (opcional) e o armazenamento persistente.
"""

from typing import List
from src.common.constants import AMASK

class MainMemory:
    def __init__(self, size: int = 4096):
        """
        Inicializa a memória com 'size' palavras de 16 bits.
        Padrão MIC-1: 4096 palavras (endereçamento de 12 bits).
        """
        self.size = size
        # Array de inteiros inicializado com 0
        self._store: List[int] = [0] * self.size

    def read(self, address: int) -> int:
        """Lê uma palavra única da memória."""
        self._validate_address(address)
        return self._store[address]

    def write(self, address: int, value: int):
        """Escreve uma palavra na memória."""
        self._validate_address(address)
        self._store[address] = value & 0xFFFF  # Garante 16 bits

    def read_block(self, start_address: int, block_size: int) -> List[int]:
        """
        Lê um bloco contínuo de memória (usado para preencher a Cache).
        Retorna uma lista de inteiros.
        """
        block = []
        for i in range(block_size):
            addr = start_address + i
            if addr < self.size:
                block.append(self._store[addr])
            else:
                block.append(0) # Padding se passar do fim da memória
        return block

    def load_program(self, program_data: List[int], start_address: int = 0):
        """Carrega um binário (lista de inteiros) na memória."""
        for i, instruction in enumerate(program_data):
            if start_address + i < self.size:
                self._store[start_address + i] = instruction
            else:
                raise ValueError("Programa excede o tamanho da memória.")

    def _validate_address(self, address: int):
        if not (0 <= address < self.size):
            raise ValueError(f"Endereço de memória inválido: {hex(address)}")

    def dump(self, start: int, length: int) -> List[int]:
        """Retorna uma fatia da memória para visualização/debug."""
        return self._store[start : start + length]