import tweepy

API_KEY = "HVuXNxP3phf0x0K8fx6nuw83M"
API_SECRET = "PW4qSl5fESGCNlCHyyNEI0jqQSNFWGKQXq6EqewexDAhJJxsfi"
ACCESS_TOKEN = "1992821684878118912-R7utlwpPRl9cstmtDS5CrUMbe9VzqD"
ACCESS_TOKEN_SECRET = "gEhpsfjbnAhmTKSfL4mx6yMilM2Uk21QbtstzQQ3prunh"

client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

def publicar_resultado(usuario, puntaje, dificultad=None, top=None):

    texto = f"🎮 {usuario} logró {puntaje} pts en Avatar vs Rooks ({dificultad}).\n"

    if top:
        texto += "🏆 Top 10 del nivel:\n"
        for pos, r in enumerate(top, start=1):
            texto += f"{pos}. {r['nombre']} - {r['puntaje']} pts\n"
    try:
        resp = client.create_tweet(text=texto)
        print("✅ Tweet enviado con éxito. ID del tweet:", resp.data["id"])
    except Exception as e:
        print("⚠️ Error al enviar el tweet:", e)