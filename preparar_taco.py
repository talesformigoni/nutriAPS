import pandas as pd

CAMINHO_XLSX = "dados/Taco-4a-Edicao.xlsx"
CAMINHO_CSV_SAIDA = "dados/alimentos_taco_base.csv"

def preparar_tabela_taco():
    # usa a segunda linha como cabeçalho
    df = pd.read_excel(CAMINHO_XLSX, header=1)

    print("Colunas encontradas na planilha depois do ajuste de header:")
    print(df.columns.tolist())

    # mapeamento baseado nas colunas que o pandas mostrou
    col_desc = "Unnamed: 1"      # coluna de 'Descrição dos alimentos'
    col_energia = "Energia"      # 'Energia (kcal)' ficou como 'Energia'
    col_cho = "idrato"           # coluna do 'Carboidrato (g)'
    col_prot = "Proteína"
    col_lip = "Lipídeos"

    colunas = [col_desc, col_energia, col_cho, col_prot, col_lip]
    df_base = df[colunas].copy()

    # renomeia para nomes amigáveis pro app
    df_base.columns = [
        "alimento",
        "energia_kcal_100g",
        "carboidratos_g_100g",
        "proteinas_g_100g",
        "lipidios_g_100g",
    ]

    # tira linhas sem nome de alimento
    df_base = df_base.dropna(subset=["alimento"])

    df_base.to_csv(CAMINHO_CSV_SAIDA, index=False, encoding="utf-8")
    print(f"Arquivo salvo em {CAMINHO_CSV_SAIDA} com {len(df_base)} alimentos.")

if __name__ == "__main__":
    preparar_tabela_taco()