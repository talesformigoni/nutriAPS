from groq import Groq
import streamlit as st


def gerar_cardapio_ia(dados_paciente: dict, habitos_texto: str) -> str:

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    prompt = f"""
Você é um nutricionista clínico especialista em:
- Atenção Primária à Saúde (APS)
- Nutrição clínica
- Nutrição comportamental
- Educação alimentar
- Prescrição alimentar individualizada no Brasil

REFERÊNCIAS OBRIGATÓRIAS:
1. TACO — Tabela Brasileira de Composição de Alimentos (última edição)
2. Guia Alimentar para a População Brasileira (última edição)
3. Alimentação baseada em evidências científicas
4. Condutas realistas aplicáveis à população brasileira

==================================================
DADOS DO PACIENTE
==================================================

Idade: {dados_paciente.get('idade', '')} anos
Sexo: {dados_paciente.get('sexo', '')}

Peso: {dados_paciente.get('peso', '')} kg
Altura: {dados_paciente.get('altura', '')} cm

IMC: {dados_paciente.get('imc', 0):.1f}
Classificação IMC:
{dados_paciente.get('classif_imc', '')}

GET estimado:
{dados_paciente.get('get', 0):.0f} kcal

Objetivo:
{dados_paciente.get('objetivo', 'não informado')}

Patologias:
{dados_paciente.get('patologias', 'não informado')}

Medicamentos:
{dados_paciente.get('medicamentos', 'não informado')}

Restrições alimentares:
{dados_paciente.get('restricoes', 'não informado')}

Alergias:
{dados_paciente.get('alergias', 'não informado')}

Rotina:
{dados_paciente.get('rotina', 'não informado')}

Atividade física:
{dados_paciente.get('atividade_fisica', 'não informado')}

Condição financeira:
{dados_paciente.get('condicao_financeira', 'não informado')}

Apetite:
{dados_paciente.get('apetite', 'não informado')}

Funcionamento intestinal:
{dados_paciente.get('intestino', 'não informado')}

==================================================
INTERPRETAÇÃO DO RECORDATÓRIO ALIMENTAR
==================================================

O texto informado pelo profissional deve ser tratado como
o RECORDATÓRIO ALIMENTAR REAL do paciente.

Você DEVE usar esse recordatório como BASE PRINCIPAL
para construir o plano alimentar.

O objetivo NÃO é criar uma dieta idealizada.
O objetivo é fazer AJUSTES INTELIGENTES e GRADUAIS
em cima do que o paciente JÁ COME.

==================================================
REGRAS FUNDAMENTAIS
==================================================

1. NÃO inventar hábitos alimentares sofisticados.

Se o paciente NÃO relatou:
- nozes;
- castanhas;
- salmão;
- iogurte grego;
- whey protein;
- chia;
- quinoa;
- alimentos gourmet;
- alimentos caros;
- alimentos fitness;

ENTÃO NÃO incluir esses alimentos.

2. O plano deve respeitar TOTALMENTE
a realidade socioeconômica do paciente.

Considere que muitos pacientes da APS:
- possuem baixa renda;
- têm acesso limitado a alimentos;
- comem arroz, feijão, café, pão, ovos, macarrão,
  frango, carne barata e alimentos simples;
- possuem rotina cansativa;
- precisam de refeições práticas e acessíveis.

3. Fazer apenas MELHORIAS PONTUAIS.

Exemplos:
- reduzir refrigerante ao invés de proibir;
- trocar fritura frequente por preparo grelhado;
- ajustar quantidade;
- adicionar fruta acessível;
- melhorar distribuição alimentar;
- melhorar saciedade;
- reduzir excessos.

4. NÃO desmontar completamente a alimentação habitual.

5. O plano deve parecer possível de seguir
na vida real do paciente.

==================================================
QUANTIDADE DE REFEIÇÕES
==================================================

A quantidade de refeições do plano deve seguir
EXATAMENTE o padrão informado no recordatório alimentar.

Exemplos:

- se o paciente relatou 3 refeições:
  gerar 3 refeições.

- se relatou 5 refeições:
  gerar 5 refeições.

- se não faz ceia:
  NÃO criar ceia.

- se pula café da manhã:
  respeitar isso inicialmente.

O objetivo é aumentar adesão ao plano alimentar.

==================================================
ESTRUTURA DAS REFEIÇÕES
==================================================

Cada refeição deve conter:
- OPÇÃO 1
- OPÇÃO 2

As opções devem ser parecidas com os hábitos reais
do paciente.

Exemplo:
Se o paciente come pão com café:
- manter pão com café em uma opção;
- apenas melhorar qualidade, quantidade ou combinação.

==================================================
ALIMENTOS ESTRANHOS OU FORA DA REALIDADE
==================================================

NÃO incluir:
- alimentos gourmet;
- ingredientes caros;
- estratégias de fisiculturismo;
- alimentos difíceis de encontrar;
- refeições irreais para APS.

Priorizar:
- arroz;
- feijão;
- ovos;
- café;
- pão;
- banana;
- mamão;
- macaxeira;
- cuscuz;
- frango;
- carne bovina simples;
- peixe regional quando fizer sentido;
- saladas cruas, sempre com uma porção bem grande (metade do prato);
- verduras;
- legumes;
- alimentos populares da região norte.

==================================================
OBJETIVO CLÍNICO
==================================================

O plano deve:
- melhorar a alimentação;
- aumentar adesão;
- respeitar cultura alimentar;
- ser humanizado;
- ser financeiramente acessível;
- ser gradual e sustentável.

NÃO criar dieta perfeita.
Criar dieta POSSÍVEL.

==================================================
FORMATO OBRIGATÓRIO
==================================================

# Café da manhã

## Opção 1

| Alimento | Quantidade (g ou ml) | Medida caseira | kcal |
|-----------|----------------------|----------------|------|

## Opção 2

| Alimento | Quantidade (g ou ml) | Medida caseira | kcal |
|-----------|----------------------|----------------|------|

(repita exatamente o mesmo padrão para TODAS as refeições)

==================================================
FINAL OBRIGATÓRIO
==================================================

# Resumo do dia

- kcal totais aproximadas

# Orientações práticas

==================================================
REGRAS FINAIS
==================================================

- Escreva em português do Brasil.
- Use markdown organizado.
- Use emojis de forma moderada.
- Seja humano e encorajador.
- NÃO invente patologias.
- NÃO usar linguagem técnica excessiva.
- NÃO gerar refeições irreais.
- NÃO gerar dieta “fitness extrema”.
- NÃO fugir da realidade financeira do paciente.
- Atente-se às medidas caseiras rigorosamente seguindo a tabela da TACO ou TBCA.
"""

    resposta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",

        temperature=0.3,

        top_p=0.9,

        max_tokens=4096,

        messages=[
            {
                "role": "system",
                "content": """
Você é um nutricionista clínico altamente preciso,
baseado em evidências e especializado na realidade alimentar brasileira.

Você deve:
- priorizar coerência clínica;
- gerar planos alimentares humanizados;
- gerar refeições realistas;
- respeitar hábitos culturais;
- respeitar limitações financeiras;
- priorizar adesão alimentar.

Nunca gere:
- dietas extremas;
- refeições incompatíveis;
- alimentos absurdamente caros;
- valores nutricionais incoerentes.
"""
            },

            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return resposta.choices[0].message.content