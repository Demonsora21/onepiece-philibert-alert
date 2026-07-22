import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime


URL = "https://www.philibertnet.com/fr/15860-one-piece-le-jeu-de-cartes"

HISTORY_FILE = "products.json"

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def get_products():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    products = []

    for item in soup.select(".product-miniature"):

        name = item.get_text(
            " ",
            strip=True
        )

        if name:
            products.append(name)

    return sorted(list(set(products)))


def load_history():

    if not os.path.exists(HISTORY_FILE):
        return []

    with open(
        HISTORY_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def save_history(products):

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            products,
            file,
            indent=2,
            ensure_ascii=False
        )


def send_discord(message):

    if not DISCORD_WEBHOOK:
        print("Discord non configuré")
        return

    requests.post(
        DISCORD_WEBHOOK,
        json={
            "content": message
        },
        timeout=10
    )


def send_telegram(message):

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram non configuré")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    requests.post(
        url,
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        },
        timeout=10
    )


def main():

    send_telegram("🏴‍☠️ Test Telegram OK")
    send_discord("🏴‍☠️ Test Discord OK")

    print("Vérification Philibert...")

    current_products = get_products()

    old_products = load_history()

    new_items = [
        product
        for product in current_products
        if product not in old_products
    ]

    if new_items:

        message = "🏴‍☠️ Nouveau produit One Piece détecté !\n\n"

        for item in new_items:
            message += f"• {item}\n"

        message += (
            "\n🔗 https://www.philibertnet.com/fr/15860-one-piece-le-jeu-de-cartes"
            f"\n\n🕒 {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )

        print(message)

        send_discord(message)
        send_telegram(message)

    else:

        print("Aucune nouveauté détectée.")

    save_history(current_products)


if __name__ == "__main__":
    main()
