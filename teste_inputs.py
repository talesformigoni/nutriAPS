import streamlit as st

st.title("Teste de Inputs")

nome = st.text_input("Nome Completo")
idade = st.number_input("Idade", min_value=0, max_value=120, step=1)
peso = st.number_input("Peso (kg)", min_value=1.0, max_value=300.0, step=0.5)

st.write("Nome:", nome)
st.write("Idade:", idade)
st.write("Peso:", peso)