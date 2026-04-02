"""
Divya scraper — sin Playwright, solo requests + BeautifulSoup
Laravel session + XSRF token handling
"""
import requests
import urllib.parse
from bs4 import BeautifulSoup


def get_divya_report(date_from: str, date_until: str, user: str, password: str) -> dict:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Accept-Language": "es-MX,es;q=0.9",
    })

    # 1. GET login page — obtener cookies XSRF + session
    session.get("https://pos.divya.com.mx/auth/login", timeout=30)
    xsrf = session.cookies.get("XSRF-TOKEN", "")

    # 2. POST login
    login_resp = session.post(
        "https://pos.divya.com.mx/auth/login",
        data={
            "email": user,
            "password": password,
            "location": "",
        },
        headers={
            "Referer": "https://pos.divya.com.mx/auth/login",
            "X-XSRF-TOKEN": urllib.parse.unquote(xsrf),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=30,
        allow_redirects=True,
    )

    if "/auth/login" in login_resp.url:
        return {"error": "Login fallido — credenciales incorrectas"}

    # 3. GET reporte
    report_url = f"https://pos.divya.com.mx/sales/general-report?from={date_from}&until={date_until}&type=all"
    report_resp = session.get(report_url, timeout=60)

    if report_resp.status_code != 200:
        return {"error": f"HTTP {report_resp.status_code} al obtener reporte"}

    # 4. Parsear tabla
    soup = BeautifulSoup(report_resp.text, "html.parser")
    tables = soup.find_all("table")

    if not tables:
        return {"error": "No se encontró tabla en el reporte", "html": report_resp.text[:2000]}

    # Extraer datos de la tabla principal
    rows = []
    for table in tables:
        headers = []
        for th in table.find_all("th"):
            headers.append(th.get_text(strip=True))

        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if cells:
                if headers:
                    row = dict(zip(headers, cells))
                else:
                    row = cells
                rows.append(row)

    return {
        "status": "ok",
        "from": date_from,
        "until": date_until,
        "rows": rows,
        "total_rows": len(rows),
    }
