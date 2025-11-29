import unittest
from src.hardware.cpu.registers import Registers
from src.hardware.cpu.datapath import Datapath
from src.hardware.cpu.control import ControlSignals
from src.common.constants import ALUOp, ShifterOp

class TestDatapathIntegration(unittest.TestCase):
    
    def setUp(self):
        self.regs = Registers()
        self.datapath = Datapath(self.regs)

    def create_signals(self, **kwargs):
        """Helper para criar sinais de controle com valores padrão (tudo zero/falso)."""
        defaults = {
            'amux': 0, 'cond': 0, 'alu': 0, 'sh': 0,
            'mbr': False, 'mar': False, 'rd': False, 'wr': False, 'enc': False,
            'c': 0, 'b': 0, 'a': 0, 'addr': 0
        }
        defaults.update(kwargs)
        return ControlSignals(**defaults)

    def test_increment_pc(self):
        """
        Teste Fundamental: PC = PC + 1
        Simula o ciclo de busca onde o Program Counter é incrementado.
        """
        # Configuração Inicial
        self.regs.PC = 10
        
        # Sinais de Controle para: PC = PC + 1
        # Barramento A lê PC (Index 2)
        # Barramento B lê Constante +1 (Index 8)
        # ULA faz SOMA (ADD)
        # Deslocador não faz nada
        # Barramento C escreve em PC (Index 2)
        # ENC (Enable C) deve estar ativo
        signals = self.create_signals(
            a=2,            # Lê PC
            b=8,            # Lê +1 (Constante)
            alu=ALUOp.ADD.value,
            sh=ShifterOp.NO_SHIFT.value,
            c=2,            # Escreve em PC
            enc=True
        )

        # Executa o ciclo
        self.datapath.run_cycle(signals)

        # Validação
        self.assertEqual(self.regs.PC, 11, "O PC deveria ter sido incrementado de 10 para 11.")

    def test_load_mbr_to_ac(self):
        """
        Teste de Caminho de Dados: AC = MBR
        Testa o uso do Multiplexador AMUX (Selecionar MBR em vez de registrador).
        """
        self.regs.MBR = 0x55
        self.regs.AC = 0x00

        # Sinais: 
        # AMUX=1 (Força entrada A ser o MBR)
        # ALU=Identity (Passa A direto)
        # C=4 (Escreve em AC)
        signals = self.create_signals(
            amux=1,             # Seleciona MBR
            alu=ALUOp.IDENTITY.value,
            c=4,                # Endereço do AC
            enc=True
        )

        self.datapath.run_cycle(signals)
        
        self.assertEqual(self.regs.AC, 0x55, "O AC deveria ter recebido o valor do MBR.")

    def test_alu_flags_update(self):
        """
        Teste de Flags: Verifica se a ULA atualiza N e Z dentro do Datapath.
        Operação: AC = -1 (Deve ativar N)
        """
        # AC = 0 + (-1)
        signals = self.create_signals(
            a=7, # Lê 0 (Constante)
            b=9, # Lê -1 (Constante)
            alu=ALUOp.ADD.value,
            c=4, # AC
            enc=True
        )
        
        self.datapath.run_cycle(signals)
        
        self.assertEqual(self.regs.AC, 0xFFFF, "AC deveria ser -1 (0xFFFF).")
        self.assertTrue(self.datapath.alu.N, "Flag N deveria estar True para resultado negativo.")
        self.assertFalse(self.datapath.alu.Z, "Flag Z deveria estar False.")

if __name__ == '__main__':
    unittest.main()