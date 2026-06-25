from groq import Groq
import json

GROQ_KEY = os.environ.get("GROQ_KEY")

cliente = Groq(api_key=GROQ_KEY)

FERRAMENTAS = [
    {
        "type": "function",
        "function": {
            "name": "buscar_web",
            "description": "Busca informações atuais na internet sobre qualquer assunto",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "O que buscar na web"
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
                        "description": "Expressão matemática para calcular. Exemplo: 2 + 2"
                    }
                },
                "required": ["expressao"]
            }
        }
    }
]

SERPER_KEY = "f424cbee899bf0d265c012268741eddbde1e0c0d"

def buscar_web(query):
    print(f"  [ferramenta] buscando: {query}")
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
    print(f"  [ferramenta] calculando: {expressao}")
    try:
        resultado = eval(expressao)
        return f"Resultado: {resultado}"
    except:
        return "Erro no cálculo"

def executar_ferramenta(nome, argumentos):
    if nome == "buscar_web":
        return buscar_web(argumentos["query"])
    elif nome == "calcular":
        return calcular(argumentos["expressao"])

def agente(pergunta):
    print(f"\nPergunta: {pergunta}")
    print("-" * 40)
    
    mensagens = [
        {"role": "system", "content": "Você é um assistente inteligente. Use as ferramentas disponíveis para responder com precisão. Pense passo a passo. Importante: ao usar a ferramenta buscar_web, escreva a query sempre em inglês e sem acentos."},
        {"role": "user", "content": pergunta}
    ]
    
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
                
                print(f"\nAgente decidiu usar: {nome}")
                resultado = executar_ferramenta(nome, argumentos)
                print(f"  [resultado] {resultado}")
                
                mensagens.append({"role": "assistant", "content": None, "tool_calls": [tool_call]})
                mensagens.append({"role": "tool", "tool_call_id": tool_call.id, "content": resultado})
        else:
            print(f"\nResposta final: {mensagem.content}")
            break

pergunta = input("\nO que você quer saber?")
agente(pergunta)