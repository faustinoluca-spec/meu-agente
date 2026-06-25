import requests
from groq import Groq

GROQ_KEY = os.environ.get("GROQ_KEY")
SERPER_KEY = os.environ.get("SERPER_KEY")

cliente = Groq(api_key=GROQ_KEY)

def buscar_web(query):
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

def chamar_agente(nome, instrucao, conteudo):
    print(f"\n[{nome}] trabalhando...")
    resposta = cliente.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": instrucao},
            {"role": "user", "content": conteudo}
        ]
    )
    resultado = resposta.choices[0].message.content
    print(f"[{nome}] concluido!")
    return resultado

def agente_pesquisador(tema):
    print("\n--- PESQUISADOR ---")
    noticias = buscar_web(f"{tema} latest news 2026")
    instrucao = "Voce e um pesquisador especialista. Organize as informacoes encontradas de forma clara, destacando os fatos mais relevantes e recentes."
    return chamar_agente("Pesquisador", instrucao, f"Tema: {tema}\n\nDados encontrados:\n{noticias}")

def agente_analista(tema, pesquisa):
    print("\n--- ANALISTA ---")
    instrucao = "Voce e um analista senior. Com base na pesquisa fornecida, faca uma analise profunda: identifique tendencias, impactos e oportunidades. Seja detalhado e preciso."
    return chamar_agente("Analista", instrucao, f"Tema: {tema}\n\nPesquisa:\n{pesquisa}")

def agente_escritor(tema, pesquisa, analise):
    print("\n--- ESCRITOR ---")
    instrucao = "Voce e um escritor profissional. Com base na pesquisa e analise fornecidas, redija um relatorio completo, bem estruturado e de facil leitura. Use titulos, subtitulos e paragrafos claros."
    return chamar_agente("Escritor", instrucao, f"Tema: {tema}\n\nPesquisa:\n{pesquisa}\n\nAnalise:\n{analise}")

def orquestrador(tema):
    print(f"\nOrquestrador iniciado para o tema: {tema}")
    print("=" * 50)

    pesquisa = agente_pesquisador(tema)
    analise = agente_analista(tema, pesquisa)
    relatorio = agente_escritor(tema, pesquisa, analise)
    revisao = agente_revisor(tema, relatorio)

    print("\n" + "=" * 50)
    print("RELATORIO FINAL")
    print("=" * 50)
    print(revisao)

    with open("relatorio.txt", "w", encoding="utf-8") as f:
        f.write(revisao)
    print("\nRelatorio salvo em relatorio.txt!")
    
def agente_revisor(tema, relatorio):
    print("\n--- REVISOR ---")
    instrucao = """Você é um editor sênior com 20 anos de experiência em jornalismo e produção de conteúdo.
Você recebeu um relatório escrito por outro agente e sua tarefa é revisá-lo criticamente.
Analise o relatório considerando:
1. CLAREZA — o texto está claro e fácil de entender?
2. COMPLETUDE — faltou alguma informação importante sobre o tema?
3. ESTRUTURA — os títulos e parágrafos estão bem organizados?
4. PRECISÃO — há afirmações vagas ou sem embasamento?
Após a análise, reescreva o relatório corrigindo todos os problemas encontrados. O resultado final deve ser a versão melhorada e definitiva do relatório, não apenas uma lista de sugestões."""
    return chamar_agente("Revisor", instrucao, f"Tema: {tema}\n\nRelatório:\n{relatorio}")
    
    
    pesquisa = agente_pesquisador(tema)
    analise = agente_analista(tema, pesquisa)
    relatorio = agente_escritor(tema, pesquisa, analise)
 

    print("\n" + "=" * 50)
    print("RELATORIO FINAL")
    print("=" * 50)
    print(relatorio)

    with open("relatorio.txt", "w", encoding="utf-8") as f:
        f.write(relatorio)
    print("\nRelatorio salvo em relatorio.txt!")

tema = input("\nSobre qual tema quer o relatorio? ")
orquestrador(tema)