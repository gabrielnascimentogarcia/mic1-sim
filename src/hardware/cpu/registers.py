"""
Implementação do Banco de Registradores do MIC-1.
Simula o comportamento de registradores de 16 bits com truncamento automático (overflow).
"""

from src.common.constants import MASK_16BIT

class Registers:
    def __init__(self):
        # Inicializa todos os registradores com 0.
        # Fonte: Diagrama "Via de Dados - MIC-1" 
        
        # Registradores visíveis ao programador (MAC-1)
        self.PC = 0   # Program Counter (12 bits efetivos, mas armazenado em 16) [cite: 2327]
        self.AC = 0   # Accumulator [cite: 2328]
        self.SP = 0   # Stack Pointer [cite: 2302]
        
        # Registradores internos da Microarquitetura
        self.IR = 0   # Instruction Register (guarda a instrução sendo executada) [cite: 2331]
        self.TIR = 0  # Temp Instruction Register (usado na decodificação) [cite: 2332]
        self.MAR = 0  # Memory Address Register [cite: 2339]
        self.MBR = 0  # Memory Buffer Register [cite: 2343]

    def _clamp(self, value: int) -> int:
        """
        Simula o truncamento físico de 16 bits.
        Se o valor exceder 65535, os bits superiores são descartados.
        """
        return value & MASK_16BIT

    # Métodos de acesso seguro (Getters/Setters) para garantir o clamp
    
    def read(self, register_name: str) -> int:
        """Lê o valor de um registrador pelo nome (string)."""
        if hasattr(self, register_name):
            return getattr(self, register_name)
        raise ValueError(f"Registrador {register_name} não existe na arquitetura MIC-1.")

    def write(self, register_name: str, value: int):
        """Escreve um valor num registrador, aplicando a máscara de 16 bits."""
        if hasattr(self, register_name):
            clamped_value = self._clamp(value)
            setattr(self, register_name, clamped_value)
        else:
            raise ValueError(f"Registrador {register_name} não existe na arquitetura MIC-1.")

    def debug_state(self) -> dict:
        """Retorna um dicionário com o estado atual para visualização/debug."""
        return {
            "PC": self.PC,
            "AC": self.AC,
            "SP": self.SP,
            "IR": self.IR,
            "TIR": self.TIR,
            "MAR": self.MAR,
            "MBR": self.MBR
        }