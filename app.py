"""
lia-browser — Servicio de scraping con Playwright para Lia
"""
import os
import json
from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

app = Flask(__name__)

API_KEY = os.environ.get("LIA_BROWSER_KEY", "")


def check_auth(req):
    if not API_KEY:
        return True
    return req.headers.get("X-API-Key") == API_KEY


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

    url = f"https://pos.divya.com.mx/sales/general-report?from={date_from}&until={date_until}&type=all"
    user = os.environ.get("DIVYA_USER", "alfredo")
    password = os.environ.get("DIVYA_PASSWORD", "")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # Navegar — redirige a login automáticamente
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle", timeout=60000)

            # Login si es necesario
            if "/auth/login" in page.url or "/login" in page.url:
                page.fill('input[name="username"], input[type="text"]', user)
                page.fill('input[name="password"], input[type="password"]', password)
                page.click('button[type="submit"]')
                page.wait_for_load_state("networkidle", timeout=60000)

            # Esperar tabla de resultados
            page.wait_for_timeout(5000)
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "html.parser")
        return jsonify({
            "status": "ok",
            "from": date_from,
            "until": date_until,
            "html": str(soup)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/scrape/raw", methods=["POST"])
def scrape_raw():
    """Scraping genérico — cualquier URL"""
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json or {}
    url = data.get("url")
    if not url:
        return jsonify({"error": "Falta parámetro: url"}), 400

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return jsonify({"status": "ok", "url": url, "text": text[:10000]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
