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