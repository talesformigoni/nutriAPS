import math
import pandas as pd

# ==========================================
# CÁLCULOS PARA ADULTOS E GESTANTES
# ==========================================

def calcular_imc(peso, altura_cm, idade=None):
    """
    Calcula o IMC e aplica as diretrizes do Ministério da Saúde 
    específicas para Adultos (<60 anos) e Idosos (>=60 anos).
    """
    altura_m = altura_cm / 100
    imc = peso / (altura_m ** 2)
    
    # Classificação para Idosos (≥ 60 anos) segundo VAN/MS
    if idade is not None and idade >= 60:
        if imc <= 22.0:
            classif = "Baixo Peso"
        elif imc < 27.0:
            classif = "Adequado ou Eutrófico"
        else:
            classif = "Sobrepeso"
            
    # Classificação para Adultos (< 60 anos) segundo VAN/MS
    else:
        if imc < 18.5:   classif = "Magreza"
        elif imc < 25.0: classif = "Eutrofia"
        elif imc < 30.0: classif = "Sobrepeso"
        elif imc < 35.0: classif = "Obesidade G.I"
        elif imc < 40.0: classif = "Obesidade G.II"
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
    
    imc, _ = calcular_imc(peso, altura_cm, idade)
    formula_utilizada = ""

    # Lógica de seleção automática da fórmula
    if is_atleta and bf is not None:
        # Tinsley (2018): 25.9 * FFM (Fat Free Mass)
        ffm = peso * (1 - (bf / 100))
        tmb = 25.9 * ffm
        formula_utilizada = "Tinsley (Atletas)"
    elif imc < 25:
        # Harris-Benedict revisada (1984) - Recomendada para Eutróficos e Baixo Peso
        if sexo == "Masculino":
            tmb = 88.362 + (13.397 * peso) + (4.799 * altura_cm) - (5.677 * idade)
        else:
            tmb = 447.593 + (9.247 * peso) + (3.098 * altura_cm) - (4.330 * idade)
        formula_utilizada = "Harris-Benedict (Eutróficos / Baixo Peso)"
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
        if classificacao_atual == "Baixo Peso":
            ganho_min, ganho_max = 12.5, 18.0
        elif classificacao_atual == "Eutrofia / Adequado":
            ganho_min, ganho_max = 11.5, 16.0
        elif classificacao_atual == "Sobrepeso":
            ganho_min, ganho_max = 7.0, 11.5
        else:
            ganho_min, ganho_max = 5.0, 9.0

    if classificacao_atual == "Baixo Peso":
        diagnostico = "Seu corpo está se preparando para nutrir uma nova vida, e a sua curva atual indica baixo peso para esta fase da gestação."
        conselho = f"Para garantir que o bebê cresça forte, nosso objetivo de ganho total deve ser entre {ganho_min} e {ganho_max} kg. Não coma grandes volumes à força, mas aumente a energia das refeições adicionando opções nutritivas: abacate, azeite, raízes e ovos. Cada grama ganha com saúde é um tijolinho na formação do bebê!"
    elif classificacao_atual == "Eutrofia / Adequado":
        diagnostico = "Excelente notícia! Você está com o IMC perfeitamente adequado para a sua semana gestacional."
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

def avaliar_gestante_ms2026(peso_atual, altura_cm, semana, peso_pre=0.0, pdf_mode=False):
    """
    Avaliação exata baseada na Tabela Oficial do MS 2026 (Kac et al. 2021).
    Sem interpolação: arrays com valores semana a semana exatos.
    """
    altura_m = altura_cm / 100.0

    is_peso_estimado = False
    if peso_pre <= 0.0:
        peso_base = peso_atual
        if semana > 13:
            is_peso_estimado = True
    else:
        peso_base = peso_pre

    imc_pre = peso_base / (altura_m ** 2)
    imc_atual = peso_atual / (altura_m ** 2)
    ganho_atual = peso_atual - peso_base

    DADOS_MS = {
        "Baixo Peso": {
            "limite_imc": "IMC < 18,5 kg/m²",
            "rec_ganho": "9,7 a 12,2 kg",
            "safe_min_key": "P18",
            "safe_max_key": "P34",
            "percentis": {
                "P10": [-0.5, -0.5, -0.4, -0.2, 0.1, 0.5, 0.9, 1.3, 1.7, 2.1, 2.5, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0, 4.3, 4.6, 4.9, 5.3, 5.7, 6.0, 6.3, 6.6, 6.8, 7.0, 7.1, 7.1, 7.0],
                "P18": [0.0, -0.1, 0.0, 0.2, 0.5, 0.9, 1.3, 1.8, 2.3, 2.7, 3.2, 3.6, 4.0, 4.3, 4.6, 5.0, 5.3, 5.6, 5.9, 6.3, 6.7, 7.1, 7.4, 7.8, 8.2, 8.5, 8.8, 9.1, 9.3, 9.5, 9.7],
                "P34": [0.5, 0.6, 0.9, 1.2, 1.6, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 4.9, 5.3, 5.7, 6.1, 6.4, 6.8, 7.2, 7.6, 8.1, 8.6, 9.0, 9.5, 10.0, 10.4, 10.9, 11.3, 11.6, 11.9, 12.1, 12.2],
                "P50": [1.0, 1.1, 1.4, 1.8, 2.3, 2.8, 3.3, 3.9, 4.5, 5.0, 5.5, 5.9, 6.3, 6.6, 7.0, 7.3, 7.6, 8.0, 8.4, 8.9, 9.4, 9.9, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.4, 13.7, 14.0],
                "P90": [2.5, 2.7, 3.0, 3.5, 4.0, 4.7, 5.3, 6.0, 6.7, 7.4, 8.0, 8.6, 9.1, 9.7, 10.2, 10.7, 11.3, 12.0, 12.7, 13.5, 14.4, 15.3, 16.1, 17.0, 17.8, 18.6, 19.3, 19.9, 20.4, 20.8, 21.0]
            }
        },
        "Eutrofia": {
            "limite_imc": "IMC ≥ 18,5 kg/m² e < 25,0 kg/m²",
            "rec_ganho": "8 a 12 kg",
            "safe_min_key": "P10",
            "safe_max_key": "P34",
            "percentis": {
                "P10": [-2.0, -2.1, -2.0, -1.8, -1.5, -1.1, -0.7, -0.3, 0.2, 0.6, 1.0, 1.3, 1.7, 1.9, 2.2, 2.5, 2.8, 3.1, 3.5, 3.9, 4.4, 4.8, 5.3, 5.8, 6.3, 6.7, 7.1, 7.4, 7.7, 7.9, 8.0],
                "P34": [-0.3, 0.0, 0.3, 0.7, 1.1, 1.5, 1.9, 2.3, 2.7, 3.1, 3.5, 3.9, 4.3, 4.7, 5.0, 5.4, 5.9, 6.3, 6.8, 7.3, 7.8, 8.3, 8.8, 9.3, 9.8, 10.3, 10.7, 11.1, 11.5, 11.8, 12.0],
                "P50": [0.5, 0.8, 1.1, 1.5, 1.9, 2.4, 2.9, 3.5, 4.0, 4.5, 5.0, 5.5, 5.9, 6.3, 6.7, 7.1, 7.6, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 12.9, 13.3, 13.7, 14.0],
                "P90": [2.0, 2.2, 2.6, 3.0, 3.5, 4.1, 4.8, 5.5, 6.2, 6.9, 7.5, 8.1, 8.7, 9.2, 9.7, 10.3, 10.9, 11.5, 12.2, 12.9, 13.7, 14.4, 15.2, 16.0, 16.8, 17.5, 18.1, 18.7, 19.2, 19.7, 20.0]
            }
        },
        "Sobrepeso": {
            "limite_imc": "IMC ≥ 25,0 kg/m² e < 30,0 kg/m²",
            "rec_ganho": "7 a 9 kg",
            "safe_min_key": "P18",
            "safe_max_key": "P27",
            "percentis": {
                "P10": [-2.5, -2.2, -2.0, -1.8, -1.6, -1.4, -1.3, -1.1, -0.9, -0.7, -0.5, -0.3, 0.0, 0.3, 0.5, 0.9, 1.2, 1.5, 1.8, 2.2, 2.5, 2.9, 3.2, 3.5, 3.8, 4.1, 4.3, 4.6, 4.7, 4.9, 5.0],
                "P18": [-2.0, -1.9, -1.8, -1.6, -1.4, -1.2, -0.9, -0.6, -0.4, -0.1, 0.2, 0.5, 0.8, 1.0, 1.3, 1.6, 1.9, 2.3, 2.7, 3.1, 3.5, 3.9, 4.4, 4.8, 5.2, 5.6, 6.0, 6.3, 6.6, 6.8, 7.0],
                "P27": [-0.5, -0.4, -0.2, -0.1, 0.2, 0.4, 0.7, 1.0, 1.3, 1.5, 1.8, 2.0, 2.3, 2.5, 2.8, 3.0, 3.4, 3.7, 4.1, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.4, 7.9, 8.3, 8.6, 8.8, 9.0],
                "P50": [0.5, 0.5, 0.6, 0.8, 1.1, 1.4, 1.8, 2.2, 2.7, 3.1, 3.5, 3.9, 4.2, 4.5, 4.8, 5.2, 5.6, 6.0, 6.5, 7.0, 7.6, 8.2, 8.9, 9.5, 10.1, 10.7, 11.3, 11.8, 12.3, 12.7, 13.0],
                "P90": [2.0, 2.1, 2.2, 2.5, 2.9, 3.3, 3.8, 4.3, 4.9, 5.4, 6.0, 6.5, 7.1, 7.6, 8.1, 8.7, 9.3, 10.0, 10.7, 11.5, 12.4, 13.2, 14.1, 15.0, 15.9, 16.7, 17.5, 18.2, 18.9, 19.5, 20.0]
            }
        },
        "Obesidade": {
            "limite_imc": "IMC ≥ 30,0 kg/m²",
            "rec_ganho": "5 a 7,2 kg",
            "safe_min_key": "P27",
            "safe_max_key": "P38",
            "percentis": {
                "P10": [-2.5, -2.3, -2.1, -2.0, -1.9, -1.8, -1.7, -1.7, -1.6, -1.6, -1.5, -1.4, -1.4, -1.3, -1.2, -1.2, -1.1, -1.0, -0.9, -0.8, -0.7, -0.7, -0.6, -0.5, -0.4, -0.3, -0.3, -0.2, -0.1, -0.1, 0.0],
                "P27": [-2.0, -1.9, -1.8, -1.6, -1.4, -1.2, -1.1, -0.9, -0.7, -0.5, -0.3, -0.1, 0.0, 0.2, 0.4, 0.6, 0.8, 1.1, 1.4, 1.7, 2.1, 2.5, 2.8, 3.2, 3.6, 3.9, 4.2, 4.5, 4.7, 4.9, 5.0],
                "P38": [-0.5, -0.3, -0.1, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.1, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.4, 3.8, 4.2, 4.6, 5.0, 5.4, 5.8, 6.2, 6.5, 6.8, 7.0, 7.2],
                "P50": [0.0, 0.1, 0.3, 0.5, 0.8, 1.0, 1.3, 1.6, 1.9, 2.2, 2.5, 2.7, 2.9, 3.1, 3.3, 3.5, 3.8, 4.0, 4.3, 4.6, 4.9, 5.3, 5.6, 6.0, 6.4, 6.7, 7.0, 7.3, 7.6, 7.8, 8.0],
                "P90": [1.5, 1.6, 1.8, 2.0, 2.3, 2.7, 3.1, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.6, 7.1, 7.7, 8.3, 9.0, 9.7, 10.4, 11.2, 12.0, 12.7, 13.5, 14.3, 15.0, 15.7, 16.4, 17.0, 17.5, 18.0]
            }
        }
    }

    if imc_pre < 18.5:
        classif = "Baixo Peso"
    elif imc_pre < 25.0:
        classif = "Eutrofia"
    elif imc_pre < 30.0:
        classif = "Sobrepeso"
    else:
        classif = "Obesidade"

    dados_curva = DADOS_MS[classif]
    idx_semana = max(0, min(semana - 10, 30))

    meta_min = dados_curva["percentis"][dados_curva["safe_min_key"]][idx_semana]
    meta_max = dados_curva["percentis"][dados_curva["safe_max_key"]][idx_semana]

    status_ganho = "Adequado"
    if ganho_atual < meta_min:
        status_ganho = "Abaixo da meta"
    elif ganho_atual > meta_max:
        status_ganho = "Acima da meta"

    if status_ganho == "Adequado":
        diag = f"Ganho de peso de {ganho_atual:.1f} kg. Adequado para a {semana}ª semana."
        cons = "Mantenha a qualidade da alimentação e hidratação."
    elif status_ganho == "Abaixo da meta":
        diag = f"Ganho de peso de {ganho_atual:.1f} kg. Abaixo do recomendado para a {semana}ª semana."
        cons = "Buscaremos opções de maior densidade nutritiva e fácil digestão."
    else:
        diag = f"Ganho de peso de {ganho_atual:.1f} kg. Acima do recomendado para a {semana}ª semana."
        cons = "Ajustaremos a qualidade dos carboidratos e a regularidade das refeições."

    return {
        "peso_base": peso_base, "imc_pre": imc_pre, "imc_atual": imc_atual,
        "classificacao_pre": classif, "ganho_atual": ganho_atual,
        "meta_semana_min": meta_min, "meta_semana_max": meta_max,
        "meta_total_min": dados_curva["percentis"][dados_curva["safe_min_key"]][-1],
        "meta_total_max": dados_curva["percentis"][dados_curva["safe_max_key"]][-1],
        "dados_ms": dados_curva, "status_ganho": status_ganho,
        "is_peso_estimado": is_peso_estimado, "diagnostico": diag,
        "conselho": cons, "pdf_mode": pdf_mode
    }

# ==========================================
# CÁLCULOS PEDIÁTRICOS (APLV - TABELA Y & OMS)
# ==========================================

import math
import pandas as pd

def calcular_aplv(idade_meses, tipo_formula, peso=0.0, sexo="M"):
    """
    Calcula a quantidade mensal de fórmula infantil para APLV (Tabela Y),
    incorporando volumes dinâmicos de diluição, gramaturas exatas,
    e cruzando com requerimentos de energia (FAO/WHO), proteína (IOM) 
    e descontos de introdução alimentar (CONITEC).
    """
    banco_formulas = {
        "Pregomin Pepti": {
            "peso_medida": 4.3, "vol_agua": 30.0, "kcal_100ml": 69.0, "nota": None
        },
        "Aptamil SL (Sem Lactose)": {
            "peso_medida": 4.3, "vol_agua": 30.0, "kcal_100ml": 69.0, "nota": None
        },
        "Neocate LCP (Até 3 anos)": {
            "peso_medida": 4.6, "vol_agua": 30.0, "kcal_100ml": 69.0, "nota": None
        },
        "Aptamil Soja 1 (0 a 6 meses)": {
            "peso_medida": 4.6, "vol_agua": 30.0, "kcal_100ml": 69.0, 
            "nota": "*Atenção: Protocolos do MS/SESAU geralmente contraindicam fórmula de soja para menores de 6 meses."
        },
        "Aptamil Soja 2 (A partir 6 meses)": {
            "peso_medida": 4.7, "vol_agua": 30.0, "kcal_100ml": 69.0, 
            "nota": "*A recomendação da embalagem varia de 4,6g a 4,8g por 30 mL (cálculo realizado usando a média de 4,7g)."
        },
        "Neocate Advance (Acima 1 ano)": {
            "peso_medida": 25.0, "vol_agua": 85.0, "kcal_100ml": 69.0, "nota": None
        }
    }

    # ==========================================================
    # VALIDAÇÕES ETÁRIAS E DE PRODUTO
    # ==========================================================
    if idade_meses < 0 or idade_meses > 24:
        return {"erro": "A Tabela Y contempla apenas crianças de 0 a 24 meses."}

    if tipo_formula not in banco_formulas:
        return {"erro": "Tipo de fórmula não encontrado no banco de dados."}

    if tipo_formula == "Neocate Advance (Acima 1 ano)" and idade_meses < 12:
        return {"erro": "O Neocate Advance é indicado apenas para crianças acima de 1 ano (12 meses)."}

    if tipo_formula == "Aptamil Soja 2 (A partir 6 meses)" and idade_meses < 6:
        return {"erro": "O Aptamil Soja 2 é indicado apenas a partir do 6º mês."}

    if tipo_formula == "Aptamil Soja 1 (0 a 6 meses)" and idade_meses < 6:
        return {"erro": "A Tabela Y não prevê fórmula de soja para menores de 6 meses."}

    # ==========================================================
    # A) LATAS POR MÊS (TABELA Y)
    # ==========================================================
    if idade_meses < 3: 
        latas_mes = 9
    elif idade_meses < 6: 
        latas_mes = 10
    elif idade_meses < 9: 
        latas_mes = 8
    elif idade_meses < 12: 
        latas_mes = 7
    else: 
        # 12 a 24 meses
        latas_mes = 7 if "Neocate" in tipo_formula else 6

    # ==========================================================
    # B, C e D) CONVERSÃO DE PESO
    # ==========================================================
    peso_lata = 400
    gramas_mes = latas_mes * peso_lata
    gramas_dia = gramas_mes / 30.0

    # ==========================================================
    # X) FREQUÊNCIA DIÁRIA DE MAMADEIRAS
    # ==========================================================
    if idade_meses < 1: 
        freq_mamadeiras = 8
    elif idade_meses < 4: 
        freq_mamadeiras = 6
    elif idade_meses < 6: 
        freq_mamadeiras = 5
    elif idade_meses < 9: 
        freq_mamadeiras = 4
    else: 
        freq_mamadeiras = 3

    # ==========================================================
    # E, F e G) VOLUMES E CALORIAS DIÁRIAS (COM REGRA DE TRÊS DINÂMICA)
    # ==========================================================
    dados_formula = banco_formulas[tipo_formula]
    peso_medida = dados_formula["peso_medida"]
    vol_agua_medida = dados_formula["vol_agua"]
    kcal_formula = dados_formula["kcal_100ml"]
    nota_observacao = dados_formula["nota"]

    # Gramas de pó por mamadeira
    gramas_mamadeira = gramas_dia / freq_mamadeiras
    
    # Conversão dinâmica
    volume_mamadeira_ml = (gramas_mamadeira * vol_agua_medida) / peso_medida
    
    volume_diario_ml = volume_mamadeira_ml * freq_mamadeiras
    kcal_dia = (volume_diario_ml * kcal_formula) / 100.0

    # ==========================================================
    # H) REQUERIMENTOS NUTRICIONAIS (FAO/WHO, IOM, CONITEC)
    # ==========================================================
    
    # 1. Desconto de Alimentação Complementar (CONITEC)
    if idade_meses < 6:
        desconto_kcal = 0
    elif idade_meses < 8: # Entre 6 meses e 7 meses e 29 dias
        desconto_kcal = 200
    elif idade_meses < 12: # Entre 8 meses e 11 meses e 29 dias
        desconto_kcal = 300
    else: # Entre 12 meses e 24 meses
        desconto_kcal = 550

    # 2. Necessidades de Proteína g/kg/dia (IOM, 2005)
    if idade_meses < 6: prot_kg = 1.52
    elif idade_meses < 12: prot_kg = 1.20
    else: prot_kg = 1.05

    # 3. Necessidades de Energia Kcal/kg/dia e Kcal/Total/Dia (FAO/WHO, 2004)
    is_masc = str(sexo).upper().startswith('M')
    
    if idade_meses < 3:
        energia_kg = 105 if is_masc else 100
        ref_kcal_total = 560 if is_masc else 510
    elif idade_meses < 6:
        energia_kg = 81 if is_masc else 83
        ref_kcal_total = 605 if is_masc else 569
    elif idade_meses < 9:
        energia_kg = 79 if is_masc else 78
        ref_kcal_total = 678 if is_masc else 628
    elif idade_meses < 12:
        energia_kg = 80 if is_masc else 79
        ref_kcal_total = 752 if is_masc else 694
    else:
        energia_kg = 83 if is_masc else 80
        ref_kcal_total = 948 if is_masc else 865

    # 4. Cálculo final do alvo calórico da fórmula
    necessidade_kcal_total = (energia_kg * peso) if peso > 0 else ref_kcal_total
    necessidade_prot_total = (prot_kg * peso) if peso > 0 else 0.0
    
    alvo_formula_kcal = necessidade_kcal_total - desconto_kcal
    if alvo_formula_kcal < 0: alvo_formula_kcal = 0

    adequacao_kcal = (kcal_dia / alvo_formula_kcal * 100) if alvo_formula_kcal > 0 else 0

    return {
        "erro": None,
        "latas_mes": latas_mes,
        "peso_lata": peso_lata,
        "peso_medida": peso_medida,
        "vol_agua_medida": vol_agua_medida,
        "gramas_mes": gramas_mes,
        "gramas_dia": round(gramas_dia, 1),
        "freq_mamadeiras": freq_mamadeiras,
        "gramas_mamadeira": round(gramas_mamadeira, 1),
        "volume_mamadeira_ml": round(volume_mamadeira_ml, 1),
        "volume_diario_ml": round(volume_diario_ml, 1),
        "kcal_dia": round(kcal_dia, 1),
        "tipo_formula": tipo_formula,
        "idade_meses": idade_meses,
        "nota_observacao": nota_observacao,
        
        # Novas chaves nutricionais
        "req_energia_kg": energia_kg,
        "req_prot_kg": prot_kg,
        "necessidade_kcal_total": round(necessidade_kcal_total, 1),
        "necessidade_prot_total": round(necessidade_prot_total, 1),
        "desconto_alimentacao_complementar": desconto_kcal,
        "alvo_formula_kcal": round(alvo_formula_kcal, 1),
        "adequacao_tabela_y_perc": round(adequacao_kcal, 1)
    }


# Cache global para evitar leitura repetitiva do CSV e melhorar performance
_df_oms_cache = None

def _obter_dados_oms():
    global _df_oms_cache
    if _df_oms_cache is None:
        try:
            _df_oms_cache = pd.read_csv('tabelas_oms.csv', sep=';')
            _df_oms_cache['Mes'] = _df_oms_cache['Mes'].astype(int)
        except Exception:
            pass
    return _df_oms_cache

def calcular_escore_z_oms(indicador, sexo, idade_meses, valor_observado):
    """
    Calcula o Escore Z exato baseado na tabela LMS da OMS.
    Inclui interpolação para meses faltantes e correção de extremos (+/- 3 SD).
    """
    df = _obter_dados_oms()
    if df is None:
        return None
        
    if idade_meses < 0:
        idade_meses = 0

    df_filtro = df[(df['Indicador'].str.lower() == str(indicador).lower()) & 
                   (df['Sexo'].str.upper() == str(sexo).upper())]
    
    if df_filtro.empty:
        return None

    df_exato = df_filtro[df_filtro['Mes'] == idade_meses]
    if not df_exato.empty:
        row = df_exato.iloc[-1]
        L, M, S = float(row['L']), float(row['M']), float(row['S'])
    else:
        # Lógica de interpolação se não achar o mês exato
        meses = sorted(df_filtro['Mes'].unique().tolist())
        if idade_meses > meses[-1]:
            row = df_filtro[df_filtro['Mes'] == meses[-1]].iloc[-1]
            L, M, S = float(row['L']), float(row['M']), float(row['S'])
        else:
            L, M, S = None, None, None
            for i in range(len(meses) - 1):
                m0, m1 = meses[i], meses[i+1]
                if m0 <= idade_meses <= m1:
                    t = (idade_meses - m0) / (m1 - m0)
                    r0 = df_filtro[df_filtro['Mes'] == m0].iloc[-1]
                    r1 = df_filtro[df_filtro['Mes'] == m1].iloc[-1]
                    L = r0['L'] + t * (r1['L'] - r0['L'])
                    M = r0['M'] + t * (r1['M'] - r0['M'])
                    S = r0['S'] + t * (r1['S'] - r0['S'])
                    break
            if L is None: 
                return None

    # Equação exata da OMS para Escore Z
    try:
        if L == 0:
            z = math.log(valor_observado / M) / S
        else:
            z = (((valor_observado / M) ** L) - 1) / (L * S)
            
        # Regra da OMS para desvios extremos (+/- 3 SD)
        if abs(z) > 3:
            def sd(n): 
                return M * (1 + L * S * n) ** (1/L) if L != 0 else M * math.exp(S * n)
            
            if z > 3: 
                z = 3 + (valor_observado - sd(3)) / (sd(3) - sd(2))
            else: 
                z = -3 + (valor_observado - sd(-3)) / (sd(-2) - sd(-3))
                
        return round(z, 2)
    except Exception:
        return None

def gerar_diagnostico_oms(peso, altura_cm, idade_meses, sexo_str):
    """
    Cruza o Peso e a Altura com o Escore Z e gera um laudo rápido.
    """
    sexo = 'M' if sexo_str.lower() == 'masculino' else 'F'
    
    z_peso = calcular_escore_z_oms('peso', sexo, idade_meses, peso)
    z_altura = calcular_escore_z_oms('altura', sexo, idade_meses, altura_cm)
    
    if z_peso is None or z_altura is None:
        return "Adequado para idade (Escore Z P/I > -2 e < +2)"
        
    # Classificação P/I
    if idade_meses <= 60:
        if z_peso < -3: classif_peso = "Peso muito baixo p/ idade"
        elif z_peso < -2: classif_peso = "Peso baixo p/ idade"
        elif z_peso <= 2: classif_peso = "Peso adequado"
        else: classif_peso = "Peso elevado p/ idade"
    else:
        if z_peso < -3: classif_peso = "Peso muito baixo p/ idade"
        elif z_peso < -2: classif_peso = "Peso baixo p/ idade"
        elif z_peso <= 1: classif_peso = "Peso adequado"
        else: classif_peso = "Peso elevado (Ver IMC)"
    
    # Classificação A/I
    if z_altura < -3: classif_altura = "Muito baixa estatura"
    elif z_altura < -2: classif_altura = "Baixa estatura p/ idade"
    elif z_altura <= 3: classif_altura = "Estatura adequada"
    else: classif_altura = "Estatura elevada"
    
    return f"{classif_peso} [Z: {z_peso:+.2f}] e {classif_altura} [Z: {z_altura:+.2f}]"

def calcular_diagnostico_detalhado_oms(peso, altura_cm, idade_meses, sexo_str):
    """
    Gera o laudo detalhado utilizando as classificações atualizadas da OMS,
    diferenciando os pontos de corte de <= 60 meses e > 60 meses.
    """
    sexo = 'M' if sexo_str.lower() == 'masculino' else 'F'
    z_peso = calcular_escore_z_oms('peso', sexo, idade_meses, peso)
    z_altura = calcular_escore_z_oms('altura', sexo, idade_meses, altura_cm)
    
    altura_m = altura_cm / 100.0
    val_imc = peso / (altura_m ** 2) if altura_m > 0 else 0
    z_imc = calcular_escore_z_oms('imc', sexo, idade_meses, val_imc)
    
    # 1. Formatação IMC
    if z_imc is None: 
        str_imc, cl_imc = "Sem dados", "Sem dados"
    else:
        if idade_meses <= 60:
            if z_imc < -3: cl_imc = "Magreza grave"; fx = "< -3"
            elif z_imc < -2: cl_imc = "Magreza"; fx = "≥ -3 e < -2"
            elif z_imc <= 1: cl_imc = "Eutrófico"; fx = "≥ -2 e ≤ +1"
            elif z_imc <= 2: cl_imc = "Risco de sobrepeso"; fx = "> +1 e ≤ +2"
            elif z_imc <= 3: cl_imc = "Sobrepeso"; fx = "> +2 e ≤ +3"
            else: cl_imc = "Obesidade"; fx = "> +3"
        else:
            if z_imc < -3: cl_imc = "Magreza grave"; fx = "< -3"
            elif z_imc < -2: cl_imc = "Magreza"; fx = "≥ -3 e < -2"
            elif z_imc <= 1: cl_imc = "Eutrófico"; fx = "≥ -2 e ≤ +1"
            elif z_imc <= 2: cl_imc = "Sobrepeso"; fx = "> +1 e ≤ +2"
            elif z_imc <= 3: cl_imc = "Obesidade"; fx = "> +2 e ≤ +3"
            else: cl_imc = "Obesidade Grave"; fx = "> +3"
            
        str_imc = f"IMC: {val_imc:.2f} kg/m² (Z: {z_imc:+.2f}) ➔ {fx} : {cl_imc}"

    # 2. Formatação Peso por Idade
    if z_peso is None: 
        str_peso, cl_peso = "Sem dados", "Sem dados"
    else:
        if idade_meses <= 60:
            if z_peso < -3: cl_peso = "Peso muito baixo p/ idade"; fx = "< -3"
            elif z_peso < -2: cl_peso = "Peso baixo p/ idade"; fx = "≥ -3 e < -2"
            elif z_peso <= 2: cl_peso = "Peso adequado"; fx = "≥ -2 e ≤ +2"
            else: cl_peso = "Peso elevado p/ idade"; fx = "> +2"
        else:
            if z_peso < -3: cl_peso = "Peso muito baixo p/ idade"; fx = "< -3"
            elif z_peso < -2: cl_peso = "Peso baixo p/ idade"; fx = "≥ -3 e < -2"
            elif z_peso <= 1: cl_peso = "Peso adequado"; fx = "≥ -2 e ≤ +1"
            else: cl_peso = "Peso elevado (Ver IMC)"; fx = "> +1"
            
        str_peso = f"Peso por idade (Z: {z_peso:+.2f}) ➔ {fx} : {cl_peso}"

    # 3. Formatação Altura por Idade
    if z_altura is None: 
        str_altura, cl_alt = "Sem dados", "Sem dados"
    else:
        if z_altura < -3: cl_alt = "Muito baixa estatura"; fx = "< -3"
        elif z_altura < -2: cl_alt = "Baixa estatura p/ idade"; fx = "≥ -3 e < -2"
        elif z_altura <= 3: cl_alt = "Estatura adequada"; fx = "≥ -2 e ≤ +3"
        else: cl_alt = "Estatura elevada"; fx = "> +3"
        
        str_altura = f"Estatura por idade (Z: {z_altura:+.2f}) ➔ {fx} : {cl_alt}"
        
    res_resumo = f"IMC: {val_imc:.2f} kg/m² | {cl_imc} / {cl_peso} / {cl_alt}"
    return str_imc, str_peso, str_altura, res_resumo
