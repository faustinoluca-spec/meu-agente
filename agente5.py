from dotenv import load_dotenv
import os
load_dotenv()
import requests
from groq import Groq
import time

import os
GROQ_KEY = os.environ.get("GROQ_KEY")
SERPER_KEY = os.environ.get("SERPER_KEY")

cliente = Groq(api_key=GROQ_KEY)

def buscar_web(query, tentativa=1):
    print(f"  [buscando] {query} (tentativa {tentativa})")
    try:
        url = "https://google.serper.dev/search"
        headers = {"X-API-KEY": SERPER_KEY}
        payload = {"q": query, "gl": "br", "hl": "pt-br", "num": 5}
        resposta = requests.post(url, headers=headers, json=payload, timeout=10)
        dados = resposta.json()
        resultados = dados.get("organic", [])
        texto = ""
        for r in resultados:
            texto += f"- {r['title']}: {r.get('snippet', '')}\n"
        if texto:
            return texto
        raise Exception("Nenhum resultado encontrado")
    except Exception as e:
        if tentativa < 3:
            print(f"  [erro] {e}. Tentando novamente em 2 segundos...")
            time.sleep(2)
            return buscar_web(query + " news", tentativa + 1)
        return "Busca falhou apos 3 tentativas."

def chamar_ia(instrucao, conteudo):
    resposta = cliente.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": instrucao},
            {"role": "user", "content": conteudo}
        ]
    )
    return resposta.choices[0].message.content

def avaliar_resultado(objetivo, resultado):
    print("\n  [avaliador] verificando qualidade...")
    avaliacao = chamar_ia(
        "Você é um avaliador rigoroso. Avalie se o resultado atinge o objetivo. Responda APENAS com: APROVADO ou REPROVAR: [motivo]",
        f"Objetivo: {objetivo}\n\nResultado:\n{resultado}"
    )
    print(f"  [avaliador] {avaliacao}")
    return avaliacao.startswith("APROVADO")

def agente_autonomo(objetivo, max_tentativas=3):
    print(f"\nObjetivo: {objetivo}")
    print("=" * 50)

    for tentativa in range(1, max_tentativas + 1):
        print(f"\nTentativa {tentativa} de {max_tentativas}")
        print("-" * 30)

        print("\n[1] Pesquisando...")
        pesquisa = buscar_web(objetivo)

        print("\n[2] Analisando...")
        analise = chamar_ia(
            "Voce e um analista senior. Analise os dados e extraia os pontos mais importantes.",
            f"Objetivo: {objetivo}\n\nDados:\n{pesquisa}"
        )

        print("\n[3] Gerando resultado...")
        resultado = chamar_ia(
            "Voce e um especialista. Com base na analise, produza um resultado completo e detalhado que atinja o objetivo.",
            f"Objetivo: {objetivo}\n\nAnalise:\n{analise}"
        )

        print("\n[4] Avaliando resultado...")
        aprovado = avaliar_resultado(objetivo, resultado)

        if aprovado:
            print("\nObjetivo atingido!")
            print("=" * 50)
            print(resultado)
            with open("resultado_autonomo.txt", "w", encoding="utf-8") as f:
                f.write(resultado)
            print("\nResultado salvo em resultado_autonomo.txt!")
            return resultado
        else:
            if tentativa < max_tentativas:
                print(f"\nResultado insuficiente. Refazendo...")
                time.sleep(2)
            else:
                print("\nMaximo de tentativas atingido. Salvando melhor resultado...")
                with open("resultado_autonomo.txt", "w", encoding="utf-8") as f:
                    f.write(resultado)

objetivo = input("\nQual o objetivo do agente? ")
agente_autonomo(objetivo)