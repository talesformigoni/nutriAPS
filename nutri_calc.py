import math

def calcular_imc(peso, altura_cm):
    altura_m = altura_cm / 100
    imc = peso / (altura_m ** 2)
    if imc < 18.5:   classif = "Magreza"
    elif imc < 25:   classif = "Eutrofia"
    elif imc < 30:   classif = "Sobrepeso"
    elif imc < 35:   classif = "Obesidade G.I"
    elif imc < 40:   classif = "Obesidade G.II"
    else:            classif = "Obesidade G.III"
    return imc, classif

def calcular_necessidades_energeticas(peso, altura_cm, idade, sexo, atividade, is_atleta=False, bf=None):
    fat_map = {
        "Sedentario (sem exercício / trabalho sentado)": 1.2,
        "Leve (caminhada ou exercício leve 1-3x/sem)": 1.375,
        "Moderado (exercício 3-5x/sem)": 1.55,
        "Intenso (exercício pesado 6-7x/sem)": 1.725,
        "Muito Intenso (atleta / trabalho físico pesado)": 1.9,
    }
    
    imc, _ = calcular_imc(peso, altura_cm)
    formula_utilizada = ""

    # Lógica de seleção automática da fórmula
    if is_atleta and bf is not None:
        # Tinsley (2018): 25.9 * FFM (Fat Free Mass)
        ffm = peso * (1 - (bf / 100))
        tmb = 25.9 * ffm
        formula_utilizada = "Tinsley (Atletas)"
    elif imc < 25:
        # Harris-Benedict revisada (1984) - Recomendada para Eutróficos
        if sexo == "Masculino":
            tmb = 88.362 + (13.397 * peso) + (4.799 * altura_cm) - (5.677 * idade)
        else:
            tmb = 447.593 + (9.247 * peso) + (3.098 * altura_cm) - (4.330 * idade)
        formula_utilizada = "Harris-Benedict (Eutróficos)"
    else:
        # Mifflin-St Jeor - Recomendada para Sobrepeso e Obesidade
        if sexo == "Masculino":
            tmb = (10 * peso) + (6.25 * altura_cm) - (5 * idade) + 5
        else:
            tmb = (10 * peso) + (6.25 * altura_cm) - (5 * idade) - 161
        formula_utilizada = "Mifflin-St Jeor (Sobrepeso/Obesidade)"
        
    get = tmb * fat_map.get(atividade, 1.2)
    return tmb, get, formula_utilizada

def extrair_ponto(texto):
    if not texto or "(" not in texto:
        return 0
    try:
        # Busca o dígito antes de " pt"
        parte = texto.split("(")[-1]
        for char in parte:
            if char.isdigit():
                return int(char)
    except (ValueError, IndexError):
        pass
    return 0

def calcular_classificacao_atalah(peso_atual, altura_cm, semana, peso_pre=0.0):
    """
    Classifica o estado nutricional da gestante baseado no IMC Atual e 
    na semana gestacional (Atalah, 1997), com cálculo opcional de ganho de peso.
    """
    altura_m = altura_cm / 100.0
    imc_atual = peso_atual / (altura_m ** 2)
    
    # Tabela Atalah (1997): Limites INFERIORES de Eutrofia, Sobrepeso e Obesidade
    tabela_atalah = {
        1: (20.0, 25.0, 30.1), 2: (20.0, 25.0, 30.1), 3: (20.0, 25.0, 30.1),
        4: (20.0, 25.0, 30.1), 5: (20.0, 25.0, 30.1), 6: (20.0, 25.0, 30.1),
        7: (20.1, 25.0, 30.1), 8: (20.2, 25.1, 30.2), 9: (20.2, 25.2, 30.2),
        10: (20.3, 25.3, 30.3), 11: (20.4, 25.4, 30.4), 12: (20.5, 25.5, 30.4),
        13: (20.7, 25.7, 30.5), 14: (20.8, 25.8, 30.6), 15: (20.9, 25.9, 30.7),
        16: (21.1, 26.0, 30.8), 17: (21.2, 26.1, 30.9), 18: (21.3, 26.2, 31.0),
        19: (21.5, 26.3, 31.0), 20: (21.6, 26.4, 31.1), 21: (21.8, 26.5, 31.2),
        22: (21.9, 26.7, 31.3), 23: (22.1, 26.9, 31.4), 24: (22.3, 27.0, 31.6),
        25: (22.5, 27.1, 31.7), 26: (22.7, 27.3, 31.8), 27: (22.8, 27.4, 31.9),
        28: (23.0, 27.6, 32.0), 29: (23.2, 27.7, 32.1), 30: (23.4, 27.9, 32.2),
        31: (23.5, 28.0, 32.3), 32: (23.7, 28.1, 32.4), 33: (23.9, 28.2, 32.5),
        34: (24.0, 28.4, 32.6), 35: (24.2, 28.5, 32.7), 36: (24.3, 28.6, 32.8),
        37: (24.5, 28.8, 32.9), 38: (24.6, 28.9, 33.0), 39: (24.8, 29.0, 33.1),
        40: (25.0, 29.2, 33.2), 41: (25.1, 29.3, 33.3), 42: (25.1, 29.3, 33.3)
    }
    
    semana_idx = min(max(int(semana), 1), 42)
    lim_eutrofia, lim_sobrepeso, lim_obesidade = tabela_atalah[semana_idx]
    
    if imc_atual < lim_eutrofia:
        classificacao_atual = "Baixo Peso"
    elif imc_atual < lim_sobrepeso:
        classificacao_atual = "Eutrofia / Adequado"
    elif imc_atual < lim_obesidade:
        classificacao_atual = "Sobrepeso"
    else:
        classificacao_atual = "Obesidade"

    # Lógica dinâmica para Peso Pré-Gestacional (Diretrizes de Ganho de Peso Total)
    gpg = None
    imc_pre = None
    
    # Se o peso pré-gestacional foi informado, calculamos a meta ideal baseada nele
    if peso_pre > 0.0:
        imc_pre = peso_pre / (altura_m ** 2)
        gpg = peso_atual - peso_pre
        if imc_pre < 18.5:
            ganho_min, ganho_max = 12.5, 18.0
        elif imc_pre < 25.0:
            ganho_min, ganho_max = 11.5, 16.0
        elif imc_pre < 30.0:
            ganho_min, ganho_max = 7.0, 11.5
        else:
            ganho_min, ganho_max = 5.0, 9.0
    else:
        # Se não informado, estimamos a meta pelo estado atual de Atalah
        if classificacao_atual == "Baixo Peso":
            ganho_min, ganho_max = 12.5, 18.0
        elif classificacao_atual == "Eutrofia / Adequado":
            ganho_min, ganho_max = 11.5, 16.0
        elif classificacao_atual == "Sobrepeso":
            ganho_min, ganho_max = 7.0, 11.5
        else:
            ganho_min, ganho_max = 5.0, 9.0

    # Definição dos textos automatizados com base na classificação ATUAL de Atalah
    if classificacao_atual == "Baixo Peso":
        diagnostico = "Seu corpo está se preparando para nutrir uma nova vida, e a sua curva atual indica baixo peso para esta fase da gestação."
        conselho = f"Para garantir que o bebê cresça forte, nosso objetivo de ganho total deve ser entre {ganho_min} e {ganho_max} kg. Não coma grandes volumes à força, mas aumente a energia das refeições adicionando opções nutritivas: abacate, azeite, raízes e ovos. Cada grama ganha com saúde é um tijolinho na formação do bebê!"
    elif classificacao_atual == "Eutrofia / Adequado":
        diagnostico = "Excelente notícia! Você está com o IMC perfeitamente adequado para a sua semana gestacional (Curva de Atalah)."
        conselho = f"Nosso objetivo agora é manter esse equilíbrio, com um ganho de peso total entre {ganho_min} e {ganho_max} kg até o fim da gravidez. Lembre-se: você não precisa 'comer por dois', mas sim comer duas vezes melhor! Continue priorizando comida de verdade e bebendo bastante água."
    elif classificacao_atual == "Sobrepeso":
        diagnostico = "Você está com o IMC na faixa de sobrepeso para a sua idade gestacional. Seu corpo já possui uma boa reserva de energia guardada para o bebê!"
        conselho = f"Por causa dessa reserva, o ganho de peso total deve ser controlado, entre {ganho_min} e {ganho_max} kg. Isso protege você de picos de pressão e glicose. Vamos focar na qualidade: reduza doces e industrializados, e capriche nas saladas e proteínas. Faremos ajustes simples, sem passar fome."
    else:
        diagnostico = "Como o seu IMC atual indica obesidade para esta fase da gestação, a natureza já garantiu que não faltará energia armazenada para o desenvolvimento do bebê!"
        conselho = f"Nosso foco não será ganhar peso, mas nutrir seu corpo. O ganho na balança deve ser mínimo (total de {ganho_min} a {ganho_max} kg). Se o peso ficar parado em alguns meses, é um ótimo sinal! Vamos evitar açúcares e frituras, cuidando de vocês dois através de refeições caseiras nutritivas."

    return {
        "imc_atual": imc_atual,
        "imc_pre": imc_pre,
        "gpg": gpg,
        "classificacao_atual": classificacao_atual,
        "ganho_min": ganho_min,
        "ganho_max": ganho_max,
        "diagnostico": diagnostico,
        "conselho": conselho,
        "tabela_atalah": tabela_atalah
    }
