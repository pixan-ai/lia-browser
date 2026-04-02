"""
lia-browser — Servicio de scraping para Lia
Sin Playwright — usa requests + BeautifulSoup directamente
"""
import os
from flask import Flask, request, jsonify
from scraper import get_divya_report
from bs4 import BeautifulSoup
import requests as req

app = Flask(__name__)

API_KEY = os.environ.get("LIA_BROWSER_KEY", "")


def check_auth(r):
    if not API_KEY:
        return True
    return r.headers.get("X-API-Key") == API_KEY


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "lia-browser"})


@app.route("/scrape/divya", methods=["POST"])
def scrape_divya():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json or {}
    date_from = data.get("from")
    date_until = data.get("until")

    if not date_from or not date_until:
        return jsonify({"error": "Faltan parámetros: from, until"}), 400

    user = os.environ.get("DIVYA_USER", "alfredo")
    password = os.environ.get("DIVYA_PASSWORD", "")

    result = get_divya_report(date_from, date_until, user, password)
    return jsonify(result)


@app.route("/scrape/raw", methods=["POST"])
def scrape_raw():
    """Scraping genérico — cualquier URL pública"""
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json or {}
    url = data.get("url")
    if not url:
        return jsonify({"error": "Falta parámetro: url"}), 400

    try:
        resp = req.get(url, timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return jsonify({"status": "ok", "url": url, "text": text[:10000]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
