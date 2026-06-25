from groq import Groq
import json
import os

GROQ_KEY = os.environ.get("GROQ_KEY")
SERPER_KEY = os.environ.get("SERPER_KEY")
ARQUIVO_MEMORIA = "memoria.json"

cliente = Groq(api_key=GROQ_KEY)

FERRAMENTAS = [
    {
        "type": "function",
        "function": {
            "name": "buscar_web",
            "description": "Busca informações atuais na internet",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "O que buscar na web, sempre em inglês"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calcular",
            "description": "Faz cálculos matemáticos",
            "parameters": {
                "type": "object",
                "properties": {
                    "expressao": {
                        "type": "string",
                        "description": "Expressão matemática. Exemplo: 2 + 2"
                    }
                },
                "required": ["expressao"]
            }
        }
    }
]

def buscar_web(query):
    print(f"  [buscando] {query}")
    import requests
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_KEY}
    payload = {"q": query, "gl": "br", "hl": "pt-br", "num": 5}
    resposta = requests.post(url, headers=headers, json=payload)
    dados = resposta.json()
    resultados = dados.get("organic", [])
    texto = ""
    for r in resultados:
        texto += f"- {r['title']}: {r.get('snippet', '')}\n"
    return texto if texto else "Nenhum resultado encontrado."

def calcular(expressao):
    print(f"  [calculando] {expressao}")
    try:
        resultado = eval(expressao)
        return f"Resultado: {resultado}"
    except:
        return "Erro no calculo"

def executar_ferramenta(nome, argumentos):
    if nome == "buscar_web":
        return buscar_web(argumentos["query"])
    elif nome == "calcular":
        return calcular(argumentos["expressao"])

def carregar_memoria():
    if os.path.exists(ARQUIVO_MEMORIA):
        with open(ARQUIVO_MEMORIA, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_memoria(historico):
    with open(ARQUIVO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)

def agente(pergunta, historico):
    print(f"\nPergunta: {pergunta}")
    print("-" * 40)

    historico.append({"role": "user", "content": pergunta})

    mensagens = [
        {"role": "system", "content": "Voce e um assistente inteligente com memoria. Use as ferramentas para responder com precisao. Ao usar buscar_web, escreva a query em ingles."}
    ] + historico

    while True:
        resposta = cliente.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensagens,
            tools=FERRAMENTAS,
            tool_choice="auto"
        )

        mensagem = resposta.choices[0].message

        if mensagem.tool_calls:
            for tool_call in mensagem.tool_calls:
                nome = tool_call.function.name
                argumentos = json.loads(tool_call.function.arguments)
                resultado = executar_ferramenta(nome, argumentos)
                print(f"  [resultado] {resultado}")
                mensagens.append({"role": "assistant", "content": None, "tool_calls": [tool_call]})
                mensagens.append({"role": "tool", "tool_call_id": tool_call.id, "content": resultado})
        else:
            print(f"\nResposta: {mensagem.content}")
            historico.append({"role": "assistant", "content": mensagem.content})
            break

    return historico

historico = carregar_memoria()

if historico:
    print(f"Memoria carregada com {len(historico)} mensagens anteriores.")
else:
    print("Novo inicio de conversa.")

while True:
    pergunta = input("\nVoce: ")
    if pergunta.lower() in ["sair", "exit", "quit"]:
        salvar_memoria(historico)
        print("Memoria salva! Ate logo.")
        break
    historico = agente(pergunta, historico)