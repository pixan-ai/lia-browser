"""
Divya scraper — sin Playwright, solo requests + BeautifulSoup
Laravel session + XSRF token handling
"""
import requests
from bs4 import BeautifulSoup


def get_divya_report(date_from: str, date_until: str, user: str, password: str) -> dict:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Accept-Language": "es-MX,es;q=0.9",
    })

    # 1. GET login page — obtener XSRF token y session cookie
    login_page = session.get("https://pos.divya.com.mx/auth/login", timeout=30)
    soup = BeautifulSoup(login_page.text, "html.parser")

    # Extraer _token del form
    token_input = soup.find("input", {"name": "_token"})
    if not token_input:
        return {"error": "No se encontró _token en el form de login"}
    csrf_token = token_input["value"]

    # 2. POST login
    login_resp = session.post(
        "https://pos.divya.com.mx/auth/login",
        data={
            "_token": csrf_token,
            "username": user,
            "password": password,
        },
        headers={
            "Referer": "https://pos.divya.com.mx/auth/login",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=30,
        allow_redirects=True,
    )

    if "/auth/login" in login_resp.url:
        return {"error": "Login fallido — credenciales incorrectas o form cambió"}

    # 3. GET reporte
    report_url = f"https://pos.divya.com.mx/sales/general-report?from={date_from}&until={date_until}&type=all"
    report_resp = session.get(report_url, timeout=60)

    if report_resp.status_code != 200:
        return {"error": f"HTTP {report_resp.status_code} al obtener reporte"}

    return {
        "status": "ok",
        "from": date_from,
        "until": date_until,
        "html": report_resp.text
    }
