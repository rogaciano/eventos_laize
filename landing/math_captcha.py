import random
from django import forms

class MathCaptchaField(forms.CharField):
    """
    Campo de CAPTCHA matemático simples que apresenta uma operação
    matemática básica (soma) para o usuário resolver.
    """
    
    def __init__(self, *args, **kwargs):
        self.session_key = kwargs.pop('session_key', 'math_captcha_answer')
        super(MathCaptchaField, self).__init__(*args, **kwargs)
        self.widget.attrs.update({'autocomplete': 'off'})
    
    def get_math_question(self, request):
        """Gera uma pergunta matemática simples e armazena a resposta na sessão"""
        # Gerar dois números aleatórios de um dígito
        a = random.randint(1, 9)
        b = random.randint(1, 9)
        
        # Calcular a resposta
        answer = a + b
        
        # Armazenar a resposta na sessão
        request.session[self.session_key] = str(answer)
        
        # Retornar a pergunta
        return f"{a} + {b} = ?"
    
    def clean(self, value):
        """Valida a resposta do usuário"""
        value = super(MathCaptchaField, self).clean(value)
        
        # Obter a resposta correta da sessão
        request = self.widget.attrs.get('request')
        if not request:
            raise forms.ValidationError("Erro interno: solicitação não disponível")
        
        correct_answer = request.session.get(self.session_key)
        if not correct_answer:
            raise forms.ValidationError("Erro de validação: resposta não encontrada")
        
        # Verificar se a resposta está correta
        if value != correct_answer:
            raise forms.ValidationError("A resposta está incorreta. Uma nova operação foi gerada. Por favor, tente novamente.")
        
        # Limpar a resposta da sessão para evitar reutilização
        del request.session[self.session_key]
        
        return value
