"""إرسال أحداث Adjust S2S - مطابق للبوت المرجعي (صيغة GET تحسب 100%)."""
import requests
import time
from typing import Optional, Dict, Tuple

ADJ_URL = "https://s2s.adjust.com/event"


def _build_proxy(proxy: Optional[Dict]) -> Optional[Dict]:
    if not proxy:
        return None
    host = proxy.get("host", proxy.get("proxy_host", ""))
    port = proxy.get("port", proxy.get("proxy_port", ""))
    ptype = proxy.get("proxy_type", "http").lower()
    if ptype == "socks5":
        scheme = "socks5"
    else:
        scheme = "http"
    user = proxy.get("username", proxy.get("proxy_user", ""))
    password = proxy.get("password", proxy.get("proxy_pass", ""))
    if user and password:
        auth = f"{user}:{password}@"
    else:
        auth = ""
    proxy_url = f"{scheme}://{auth}{host}:{port}"
    return {"http": proxy_url, "https": proxy_url}


def send_adj(
    app_token: str,
    event_token: str,
    gps_adid: str,
    proxy: Optional[Dict] = None,
    platform: str = "android",
    idfa: str = None,
    idfv: str = None,
    level: int = None,
) -> Tuple[int, str]:
    """إرسال حدث إلى Adjust S2S API - صيغة GET (تحسب 100%) - مطابق للبوت المرجعي."""
    url = ADJ_URL

    # على iOS نستخدم idfa كـ GPS ADID (مطابق لمنطق البوت المرجعي)
    if platform == "ios" and idfa:
        adid = idfa
    else:
        adid = gps_adid

    params = {
        "app_token": app_token,
        "event_token": event_token,
        "gps_adid": adid,
        "s2s": "1",
        "created_at": int(time.time()),
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }

    print(f"[DEBUG] Adjust Request URL: {url}")
    print(f"[DEBUG] Adjust Params: {params}")

    try:
        proxies = _build_proxy(proxy)
        if proxies:
            r = requests.get(url, params=params, headers=headers, timeout=30, proxies=proxies)
        else:
            r = requests.get(url, params=params, headers=headers, timeout=30)

        print(f"[DEBUG] Adjust Response: {r.status_code} - {r.text[:200]}")

        if r.status_code == 200:
            return 200, r.text
        return r.status_code, r.text

    except Exception as e:
        print(f"[DEBUG] Adjust Exception: {e}")
        return 500, str(e)
