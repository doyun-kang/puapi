# app.py
import os
import sys
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import uvicorn

from netflix_api import (
    check_account,
    create_nftoken,
    format_expiry,
    extract_netflix_cookie_bundles,
    has_required_netflix_cookies,
)

app = FastAPI(
    title="FEDFLIX DATA API",
    description=(
        "API untuk cek akun Netflix + generate NFToken / Login Links.\n\n"
        "Cara pakai: kirim cookies Netflix via query string (GET) atau body (POST)."
    ),
    version="2.2.0",
)


# ==================== SCHEMA ====================
class CheckRequest(BaseModel):
    cookies: str | None = None
    cookiesnetscape: str | None = None
    generate_nftoken: bool = True


class LoginLinkRequest(BaseModel):
    cookies: str | None = None
    cookiesnetscape: str | None = None


# ==================== HELPER ====================
def _extract_cookies_from_payload(cookies: str = None, cookiesnetscape: str = None) -> dict:
    raw = cookiesnetscape or cookies
    if not raw or not raw.strip():
        raise HTTPException(
            status_code=400,
            detail="Cookies wajib diisi. Kirim parameter 'cookies' atau 'cookiesnetscape'.",
        )

    bundles = extract_netflix_cookie_bundles(raw)
    if not bundles:
        raise HTTPException(
            status_code=400,
            detail="Cookie Netflix tidak valid. Pastikan mengandung NetflixId.",
        )

    cookie_dict = bundles[0].get("cookies") or {}
    if not has_required_netflix_cookies(cookie_dict):
        raise HTTPException(
            status_code=400,
            detail="NetflixId tidak ditemukan di cookie yang dikirim.",
        )

    return cookie_dict


def _build_login_link_response(cookie_dict: dict) -> dict:
    token, expires = create_nftoken(cookie_dict, attempts=3)
    if not token:
        raise HTTPException(
            status_code=400,
            detail="Gagal generate NFToken. Cookies mungkin invalid / expired.",
        )

    return {
        "ok": True,
        "nftoken": token,
        "expires": expires,
        "expires_formatted": format_expiry(expires),
        "links": {
            "pc":     f"https://netflix.com/browse?nftoken={token}",
            "phone":  f"https://netflix.com/unsupported?nftoken={token}",
            "tv":     f"https://netflix.com/tv2?nftoken={token}",
            "direct": f"https://netflix.com/account?nftoken={token}",
        },
    }


# ==================== ROUTES ====================
@app.get("/")
def root():
    return {
        "service": "FEDFLIX DATA API",
        "status": "online",
        "version": "2.2.0",
        "endpoints": {
            "GET /api/giveloginlink": "Generate NFToken + login links (query string)",
            "POST /api/giveloginlink": "Generate NFToken + login links (body JSON)",
            "GET /api/check": "Cek info akun lengkap (query string)",
            "POST /api/check": "Cek info akun lengkap (body JSON)",
        },
    }


@app.get("/api/giveloginlink")
def api_giveloginlink_get(
    cookies: str | None = Query(default=None, description="Cookie Netflix"),
    cookiesnetscape: str | None = Query(default=None, description="Cookie format Netscape"),
):
    cookie_dict = _extract_cookies_from_payload(cookies, cookiesnetscape)
    return _build_login_link_response(cookie_dict)


@app.post("/api/giveloginlink")
def api_giveloginlink_post(payload: LoginLinkRequest):
    cookie_dict = _extract_cookies_from_payload(payload.cookies, payload.cookiesnetscape)
    return _build_login_link_response(cookie_dict)


@app.get("/api/check")
def api_check_get(
    cookies: str | None = Query(default=None, description="Cookie Netflix"),
    cookiesnetscape: str | None = Query(default=None, description="Cookie format Netscape"),
    generate_nftoken: bool = Query(default=True, description="Generate NFToken?"),
):
    _extract_cookies_from_payload(cookies, cookiesnetscape)
    result = check_account(
        cookies_input=cookies,
        cookiesnetscape=cookiesnetscape,
        generate_nftoken=generate_nftoken,
    )
    if not result.get("ok"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Gagal memproses akun."),
        )
    return result


@app.post("/api/check")
def api_check_post(payload: CheckRequest):
    _extract_cookies_from_payload(payload.cookies, payload.cookiesnetscape)
    result = check_account(
        cookies_input=payload.cookies,
        cookiesnetscape=payload.cookiesnetscape,
        generate_nftoken=payload.generate_nftoken,
    )
    if not result.get("ok"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Gagal memproses akun."),
        )
    return result


# ==================== PERSISTENT SERVER LAUNCHER ====================
# Kode ini memastikan Uvicorn langsung jalan dan menahan server agar tidak offline.
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 20114))
    
    print("\n" + "=" * 60)
    print("🚀 FEDFLIX DATA API BERHASIL DI-DEPLOY DI KATABUMP!")
    print(f"🔗 Cek API Endpoint: http://51.75.118.18:{port}/api/check?cookies=")
    print("=" * 60 + "\n", flush=True)
    
    try:
        uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
    except Exception as e:
        print(f"❌ Error starting server: {e}", file=sys.stderr)
        sys.exit(1)