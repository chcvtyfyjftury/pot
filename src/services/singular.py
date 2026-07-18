import requests
import logging
import time
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)

SINGULAR_URL = "https://s2s.singular.net/api/v1/evt"


def _build_proxy(proxy: Optional[Dict]) -> Optional[Dict]:
    if not proxy:
        return None
    host = proxy.get("host", "")
    port = proxy.get("port", "")
    ptype = proxy.get("proxy_type", "http").lower()
    user = proxy.get("username", "")
    password = proxy.get("password", "")
    if user and password:
        auth = f"{user}:{password}@"
    else:
        auth = ""
    proxy_url = f"{ptype}://{auth}{host}:{port}"
    return {"http": proxy_url, "https": proxy_url}


def send_singular(
    event_name: str,
    aifa: str,
    uid: str,
    package: str,
    app_key: str,
    level=None,
    proxy: Optional[Dict] = None,
    platform: str = "android",
    idfa: str = None,
    idfv: str = None,
    singular_uid: str = None,
) -> Tuple[int, str]:
    # بناء المعاملات كما في الرابط الشغال (GET request)
    params: Dict = {
        "a": app_key,
        "p": "Android",
        "i": package,
        "aifa": aifa or "",
        "u": singular_uid or uid or "",
        "utime": str(int(time.time())),
        "n": event_name,
    }

    # iOS: استخدم idfa بدل aifa
    if platform == "ios" and idfa:
        params["aifa"] = idfa
        if idfv:
            params["idfv"] = idfv

    # إضافة رقم اللفل إن وُجد
    if level is not None:
        params["level"] = str(level)

    # تنظيف المعاملات الفارغة
    params = {k: v for k, v in params.items() if v}

    headers = {
        "User-Agent": "SingularS2S/1.0",
        "Accept": "application/json",
    }

    try:
        proxies = _build_proxy(proxy)
        r = requests.get(SINGULAR_URL, params=params, headers=headers, timeout=30, proxies=proxies)
        logger.info(f"[SNG] {package} | {event_name} | status={r.status_code}")
        return r.status_code, r.text[:500]
    except Exception as e:
        logger.error(f"[SNG] Exception: {e}")
        return 500, str(e)
