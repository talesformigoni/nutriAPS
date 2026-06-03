import google.generativeai as genai

# Cole sua chave aqui diretamente só para testar
API_KEY = "AIzaSyAFvyYPjOUYl8bfRm_t2vTPzNLwCQa8hzA"

genai.configure(api_key=API_KEY)

print("\n=== MODELOS DISPONÍVEIS NA SUA CONTA ===\n")

for modelo in genai.list_models():
    # Mostra só os que suportam geração de texto
    if "generateContent" in modelo.supported_generation_methods:
        print(f"✅ {modelo.name}")

print("\n=== FIM DA LISTA ===\n")