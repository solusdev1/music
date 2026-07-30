"""Controle de qualidade da música — o que só é possível tendo o catálogo.

Com 5 músicas/dia, a ameaça real à qualidade não é a letra isolada ficar
ruim: é o acervo inteiro convergir para as mesmas imagens, as mesmas rimas
e os mesmos refrãos. Nas 5 primeiras letras do canal já aparecem
"noite" 8x, "estrada" 6x, "coração" 6x, "cheiro" 6x.

Este módulo lê TODAS as letras do catálogo e devolve o que já está gasto,
para o prompt do dia mandar evitar — em vez de descobrir na música 100.
"""

import re
import unicodedata
from collections import Counter
from pathlib import Path

# Metatags do Suno e direções de cena não são letra — não entram na análise.
_METATAG = re.compile(r"\[[^\]]*\]")

_STOPWORDS_PT = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "do", "da", "dos",
    "das", "em", "no", "na", "nos", "nas", "por", "para", "pra", "pro", "com",
    "sem", "sob", "sobre", "entre", "ate", "ate", "e", "ou", "mas", "que",
    "quem", "qual", "quando", "onde", "como", "porque", "se", "nao", "sim",
    "eu", "tu", "ele", "ela", "nos", "vos", "eles", "elas", "me", "te", "lhe",
    "nos", "vos", "lhes", "meu", "minha", "meus", "minhas", "teu", "tua",
    "seu", "sua", "seus", "suas", "nosso", "nossa", "este", "esta", "esse",
    "essa", "isso", "isto", "aquele", "aquela", "aquilo", "ja", "ainda",
    "mais", "menos", "muito", "pouco", "todo", "toda", "todos", "todas",
    "outro", "outra", "so", "tambem", "bem", "mal", "aqui", "ali", "la",
    "hoje", "ontem", "amanha", "agora", "sempre", "nunca", "antes", "depois",
    "ser", "estar", "ter", "haver", "fazer", "ir", "vir", "ver", "dar", "ficar",
    "e", "era", "foi", "sao", "esta", "estava", "tem", "tinha", "vai", "vou",
    "voce", "vc", "de", "da", "no", "na",
    # verbos comuns conjugados: são gramática, não imagem. Sem isso o relatório
    # acusa "quis", "veio", "deixou" como se fossem cenário.
    "quis", "quer", "quero", "queria", "veio", "vem", "venha", "vinha",
    "deixou", "deixa", "deixe", "deixar", "abriu", "abre", "abrir", "chamou",
    "chama", "chamar", "encontrou", "encontra", "encontrar", "levou", "leva",
    "levar", "chegou", "chega", "chegar", "passou", "passa", "passar",
    "ficou", "fica", "voltou", "volta", "voltar", "disse", "dizer", "falou",
    "falar", "sabe", "saber", "sabia", "pode", "poder", "podia", "vejo",
    "olhou", "olhar", "sentiu", "sentir", "sinto", "guardou", "guardar",
    "trouxe", "trazer", "achou", "achar", "perdeu", "perder", "pegou",
    "pegar", "coloca", "colocou", "andar", "andou", "correu", "correr",
}


_STOPWORDS_EN = {
    "the","and","but","for","nor","yet","with","that","this","these","those",
    "have","has","had","been","was","were","are","will","would","could","should",
    "there","their","them","they","then","than","when","what","which","who","whom",
    "here","from","into","onto","upon","over","under","about","after","before",
    "just","only","still","more","most","much","many","some","any","all","both",
    "each","every","other","another","same","such","own","very","too","also",
    "back","down","out","off","away","again","ever","never","always","now",
    "know","knew","think","say","said","tell","told","come","came","comin","go",
    "went","goin","get","got","give","gave","take","took","make","made","makin",
    "let","put","keep","kept","find","found","leave","left","hold","held",
    "thing","things","time","times","day","days","night","year","years","way",
    "aint","dont","cant","wont","didnt","couldnt","wouldnt","gonna","gotta",
    "walkin","talkin","lookin","standin","sittin","holdin","whole","word","words",
    "one","two","like","well","good","long","last","first","little","big","old",
    "man","men","she","her","his","him","its","our","your","you","yours",
}

# Sinaliza qual banco usar. Sem isso, letra em inglês era medida com
# stopwords em português e "more", "that", "just" apareciam como imagem.
_BANCOS = {"pt": _STOPWORDS_PT, "es": _STOPWORDS_PT, "en": _STOPWORDS_EN}


def _stopwords(idioma=None):
    if not idioma:
        return _STOPWORDS_PT | _STOPWORDS_EN
    return _BANCOS.get(str(idioma)[:2].lower(), _STOPWORDS_PT)


def _norm(word: str) -> str:
    return unicodedata.normalize("NFKD", word.lower()).encode("ascii", "ignore").decode()


def extract_lyric_text(raw: str) -> str:
    """Remove metatags [Chorus], [Slide Guitar] etc. Sobra só o que é cantado."""
    return _METATAG.sub(" ", raw)


def _content_words(text: str, idioma=None):
    stop = _stopwords(idioma)
    for w in re.findall(r"[a-zA-ZÀ-ÿ']+", extract_lyric_text(text)):
        n = _norm(w.replace("'", ""))
        if len(n) > 3 and n not in stop:
            yield n


def _load_lyrics(conn, niche):
    """Devolve [(titulo, texto)] das faixas do nicho que têm letra em disco."""
    rows = conn.execute(
        "SELECT title, lyrics_path FROM tracks WHERE niche=? AND lyrics_path IS NOT NULL",
        (niche,),
    ).fetchall()
    out = []
    for r in rows:
        p = Path(r["lyrics_path"])
        if p.exists():
            out.append((r["title"], p.read_text(encoding="utf-8", errors="replace")))
    return out


# Abaixo disto a amostra é pequena demais: 2 de 5 letras vira "40%" e o
# relatório passa a acusar coincidência como vício.
MIN_AMOSTRA = 8


def vocabulary_report(conn, niche, *, threshold=0.4, top=25, protegidas=(), idioma=None):
    """Palavras de conteúdo presentes em >= threshold das músicas do acervo.

    Usa PRESENÇA por música, não contagem bruta: uma palavra repetida 20x
    numa única letra é estilo; a mesma palavra em 8 de 10 letras é vício.

    `protegidas` são as palavras de identidade do nicho (Deus, Jesus, fé num
    canal gospel). Repetir essas não é defeito — é o assunto do canal.
    """
    letras = _load_lyrics(conn, niche)
    if not letras:
        return {"n_musicas": 0, "saturadas": [], "frequentes": [], "amostra_pequena": True}

    prot = {_norm(p) for p in protegidas}
    presenca = Counter()
    for _, texto in letras:
        for w in set(_content_words(texto, idioma)):
            if w not in prot:
                presenca[w] += 1

    n = len(letras)
    ranked = [
        {"palavra": w, "musicas": c, "pct": round(100 * c / n)}
        for w, c in presenca.most_common(top)
    ]
    return {
        "n_musicas": n,
        "amostra_pequena": n < MIN_AMOSTRA,
        "saturadas": [r for r in ranked if r["musicas"] / n >= threshold],
        "frequentes": ranked,
    }


def rhyme_report(conn, niche, *, threshold=0.4, top=15):
    """Terminações de verso repetidas no acervo (rimas viciadas).

    Considera as 3 letras finais da última palavra de cada verso — aproximação
    grosseira de rima, mas suficiente para flagrar 'ão/ção' em todo refrão.
    """
    letras = _load_lyrics(conn, niche)
    if not letras:
        return {"n_musicas": 0, "saturadas": []}

    presenca = Counter()
    for _, texto in letras:
        term = set()
        for linha in extract_lyric_text(texto).splitlines():
            palavras = re.findall(r"[a-zA-ZÀ-ÿ]+", linha)
            if palavras:
                fim = _norm(palavras[-1])
                if len(fim) >= 3:
                    term.add(fim[-3:])
        for t in term:
            presenca[t] += 1

    n = len(letras)
    return {
        "n_musicas": n,
        "saturadas": [
            {"terminacao": f"-{t}", "musicas": c, "pct": round(100 * c / n)}
            for t, c in presenca.most_common(top)
            if c / n >= threshold
        ],
    }


def title_collisions(conn, niche, *, min_overlap=2, idioma=None):
    """Títulos que dividem palavras de conteúdo — canibalizam busca entre si."""
    rows = conn.execute(
        "SELECT id, title FROM tracks WHERE niche=? AND status != 'draft'", (niche,)
    ).fetchall()
    sets = [(r["id"], r["title"], {w for w in _content_words(r["title"], idioma)}) for r in rows]

    colisoes = []
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            comum = sets[i][2] & sets[j][2]
            if len(comum) >= min_overlap:
                colisoes.append({
                    "a": sets[i][1], "b": sets[j][1],
                    "comum": sorted(comum),
                })
    return colisoes


def avoid_list(conn, niche, *, n_palavras=15, n_rimas=5, protegidas=(), min_musicas=3, idioma=None):
    """Resumo do que evitar hoje — é isto que entra no prompt de letras.

    Exige presença em pelo menos `min_musicas` letras (não só percentual):
    num acervo de 5, "2 de 5 = 40%" é coincidência, não vício.
    """
    voc = vocabulary_report(conn, niche, protegidas=protegidas, idioma=idioma)
    rim = rhyme_report(conn, niche)
    return {
        "n_musicas": voc["n_musicas"],
        "amostra_pequena": voc.get("amostra_pequena", True),
        "palavras": [r["palavra"] for r in voc["saturadas"]
                     if r["musicas"] >= min_musicas][:n_palavras],
        "rimas": [r["terminacao"] for r in rim["saturadas"]
                  if r["musicas"] >= min_musicas][:n_rimas],
    }


def format_report(conn, niche, *, protegidas=(), idioma=None):
    """Relatório legível para o comando `quality`."""
    voc = vocabulary_report(conn, niche, protegidas=protegidas, idioma=idioma)
    if voc["n_musicas"] == 0:
        return (f"Nenhuma letra em disco para o nicho {niche!r}.\n"
                "Registre com: cli.py add-song --lyrics <arquivo>")

    rim = rhyme_report(conn, niche)
    col = title_collisions(conn, niche)
    L = [f"🎼 QUALIDADE — {niche} ({voc['n_musicas']} letra(s) analisada(s))", ""]
    if voc["amostra_pequena"]:
        L += [f"ℹ️  Amostra pequena (< {MIN_AMOSTRA} letras): trate como indicativo,",
              "   não como diagnóstico. O sinal fica confiável conforme o acervo cresce.", ""]

    L.append("IMAGENS SATURADAS (presentes em ≥40% das letras)")
    if voc["saturadas"]:
        for r in voc["saturadas"]:
            L.append(f"  ⚠️  {r['palavra']:<16} {r['musicas']}/{voc['n_musicas']} letras ({r['pct']}%)")
    else:
        L.append("  ✅ nenhuma — vocabulário ainda variado")

    L += ["", "TERMINAÇÕES DE VERSO REPETIDAS"]
    if rim["saturadas"]:
        for r in rim["saturadas"]:
            L.append(f"  ⚠️  {r['terminacao']:<16} {r['musicas']}/{rim['n_musicas']} letras ({r['pct']}%)")
    else:
        L.append("  ✅ nenhuma dominante")

    L += ["", "COLISÃO DE TÍTULOS (canibalizam busca)"]
    if col:
        for c in col[:10]:
            L.append(f"  ⚠️  «{c['a']}» × «{c['b']}» → {', '.join(c['comum'])}")
    else:
        L.append("  ✅ nenhuma")

    L += ["", "PALAVRAS MAIS PRESENTES"]
    L += [f"  {r['palavra']:<16} {r['pct']:>3}%" for r in voc["frequentes"][:12]]
    return "\n".join(L)
