import unittest
from src.assembler.parser import AssemblyParser
from src.assembler.codegen import CodeGenerator
from src.assembler.isa import MAC1_INSTRUCTIONS

class TestAssemblerIntegration(unittest.TestCase):
    
    def setUp(self):
        self.parser = AssemblyParser()
        self.codegen = CodeGenerator()

    def test_full_assembly_process(self):
        """
        Teste de Integração:
        Verifica se um código fonte com Rótulos, Comentários e Instruções variadas
        gera o binário exato esperado.
        """
        
        # Código Fonte de Exemplo (MAC-1)
        source_code = """
        ; Programa de Teste
        START:  LOCO 10      ; Carrega 10 no AC
                ADDD 50      ; Soma o valor do endereço 50
        LOOP:   DESP 1       ; Decrementa SP (Instrução de Constante)
                JZER END     ; Se zero, pula para o fim
                JUMP LOOP    ; Pula de volta para LOOP
        END:    PUSH         ; Salva AC na pilha
        """

        # --- TRADUÇÃO MANUAL ESPERADA (Gabarito) ---
        # 0: START: LOCO 10  -> Op 0x7000 | 10  = 0x700A
        # 1:        ADDD 50  -> Op 0x2000 | 50  = 0x2032 (50 dec = 0x32 hex)
        # 2: LOOP:  DESP 1   -> Op 0xFE00 | 1   = 0xFE01
        # 3:        JZER END -> Op 0x5000 | 5   = 0x5005 (END está no endereço 5)
        # 4:        JUMP LOOP-> Op 0x6000 | 2   = 0x6002 (LOOP está no endereço 2)
        # 5: END:   PUSH     -> Op 0xF400       = 0xF400
        
        expected_binary = [
            0x700A,
            0x2032,
            0xFE01,
            0x5005,
            0x6002,
            0xF400
        ]

        # --- EXECUÇÃO ---
        # 1. Parse
        parsed_lines = self.parser.parse(source_code)
        
        # 2. Code Generation
        generated_binary = self.codegen.generate(parsed_lines)

        # --- VALIDAÇÃO ---
        # Compara a lista gerada com a lista esperada
        self.assertEqual(generated_binary, expected_binary, 
            f"\nEsperado: {[hex(x) for x in expected_binary]}\nGerado:   {[hex(x) for x in generated_binary]}")

    def test_forward_jump_reference(self):
        """
        Teste específico para 'Forward Reference' (Pular para um rótulo que ainda não foi definido).
        Isso valida se o Two-Pass (dois passos) do codegen está funcionando.
        """
        code = """
            JUMP TARGET   ; Pula para frente (endereço desconhecido na leitura linear)
            LOCO 0
        TARGET: PUSH
        """
        
        # 0: JUMP 2 (0x6000 | 2 = 0x6002)
        # 1: LOCO 0 (0x7000 | 0 = 0x7000)
        # 2: PUSH   (0xF400)
        expected = [0x6002, 0x7000, 0xF400]
        
        parsed = self.parser.parse(code)
        binary = self.codegen.generate(parsed)
        
        self.assertEqual(binary, expected)

if __name__ == '__main__':
    unittest.main()