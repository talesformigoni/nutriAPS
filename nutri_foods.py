import pandas as pd

CAMINHO_XLSX = "dados/Taco-4a-Edicao.xlsx"

def carregar_tabela_alimentos():
    # usa a segunda linha como cabeçalho (header=1)
    df = pd.read_excel(CAMINHO_XLSX, header=1)

    # mapeia as colunas da TACO para nomes amigáveis
    col_desc = "Unnamed: 1"   # descrição dos alimentos
    col_energia = "Energia"   # Energia (kcal)
    col_cho = "idrato"        # Carboidrato (g)
    col_prot = "Proteína"
    col_lip = "Lipídeos"

    df_base = df[[col_desc, col_energia, col_cho, col_prot, col_lip]].copy()

    df_base.columns = [
        "alimento",
        "energia_kcal_100g",
        "carboidratos_g_100g",
        "proteinas_g_100g",
        "lipidios_g_100g",
    ]

    # limpa linhas sem alimento
    df_base = df_base.dropna(subset=["alimento"])

    # garante que números são numéricos
    for col in ["energia_kcal_100g", "carboidratos_g_100g", "proteinas_g_100g", "lipidios_g_100g"]:
        df_base[col] = pd.to_numeric(df_base[col], errors="coerce")

    # remove linhas sem energia (caso exista alguma linha estranha)
    df_base = df_base.dropna(subset=["energia_kcal_100g"])

    return df_base