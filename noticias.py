import feedparser
import sqlite3
import requests
from datetime import datetime
import os


# ==============================
# CONFIGURAÇÕES
# ==============================

RSS_URL = "https://news.google.com/rss/search?q=Manaus%20crime&hl=pt-BR&gl=BR&ceid=BR:pt-419"


# Busca os dados protegidos do GitHub Secrets
TOKEN = os.environ["TOKEN_TELEGRAM"]
CHAT_ID = os.environ["CHAT_ID_TELEGRAM"]



# ==============================
# BANCO DE DADOS
# ==============================

conn = sqlite3.connect("noticias.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS noticias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT UNIQUE,
    link TEXT,
    data TEXT
)
""")

conn.commit()



# ==============================
# SALVAR NOTÍCIA
# ==============================

def salvar_noticia(titulo, link):

    try:

        cursor.execute("""
        INSERT INTO noticias
        (titulo, link, data)

        VALUES (?, ?, ?)
        """,
        (
            titulo,
            link,
            datetime.now().strftime("%d/%m/%Y %H:%M")
        ))

        conn.commit()

        return True


    except sqlite3.IntegrityError:

        return False



# ==============================
# BUSCAR NOTÍCIAS
# ==============================

feed = feedparser.parse(RSS_URL)


mensagem = f"""
🌎 BOLETIM DE MANAUS

📅 {datetime.now().strftime("%d/%m/%Y %H:%M")}

"""


contador = 0


for noticia in feed.entries:

    titulo = noticia.title.strip()
    link = noticia.link


    nova = salvar_noticia(
        titulo,
        link
    )


    if not nova:
        continue


    mensagem += f"""
📰 {titulo}


====================

"""


    contador += 1


    if contador >= 20:
        break



# ==============================
# ENVIO TELEGRAM
# ==============================

def enviar_telegram(texto):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    limite = 4000


    partes = [
        texto[i:i+limite]
        for i in range(0, len(texto), limite)
    ]


    for parte in partes:

        resposta = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": parte
            }
        )


        if resposta.status_code != 200:

            print(resposta.text)

            return False


    return True



if enviar_telegram(mensagem):

    print("Enviado com sucesso!")

else:

    print("Erro no envio!")


conn.close()
