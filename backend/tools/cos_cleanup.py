"""COS mall/products/ """
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hashlib
import hmac
import time
import httpx
import xml.etree.ElementTree as ET
from urllib.parse import quote
from config import COS_SECRET_ID, COS_SECRET_KEY, COS_BUCKET, COS_REGION

COS_ENDPOINT = f"{COS_BUCKET}.cos.{COS_REGION}.myqcloud.com"


def cos_sign(method, path, param_dict=None, expire=3600):
    key_time = f"{int(time.time())};{int(time.time())+expire}"
    sign_key = hmac.new(COS_SECRET_KEY.encode(), key_time.encode(), hashlib.sha1).hexdigest()

    param_list = ''
    param_str = ''
    if param_dict:
        sorted_keys = sorted(param_dict.keys())
        param_list = ";".join(k.lower() for k in sorted_keys)
        param_str = "&".join(f"{k.lower()}={quote(str(param_dict[k]), safe='')}" for k in sorted_keys)

    http_string = f"{method.lower()}\n{path}\n{param_str}\nhost={COS_ENDPOINT}\n"
    string_to_sign = f"sha1\n{key_time}\n{hashlib.sha1(http_string.encode()).hexdigest()}\n"
    signature = hmac.new(sign_key.encode(), string_to_sign.encode(), hashlib.sha1).hexdigest()
    return (
        f"q-sign-algorithm=sha1"
        f"&q-ak={COS_SECRET_ID}"
        f"&q-sign-time={key_time}"
        f"&q-key-time={key_time}"
        f"&q-header-list=host"
        f"&q-url-param-list={param_list}"
        f"&q-signature={signature}"
    )


def list_all_keys(prefix):
    ''"keys''"
    all_keys = []
    marker = ''
    page = 0
    while True:
        page += 1
        param_dict = {"prefix": prefix, "max-keys": "1000"}
        if marker:
            param_dict["marker"] = marker

        params = "&".join(f"{k}={quote(str(v), safe='')}" for k, v in param_dict.items())
        url = f"https://{COS_ENDPOINT}/?{params}"
        headers = {"Host": COS_ENDPOINT}
        headers["Authorization"] = cos_sign("get", "/", param_dict)

        r = httpx.get(url, headers=headers, timeout=30)
        if r.status_code != 200:
            print(f": {r.status_code}", flush=True)
            break

        root = ET.fromstring(r.text)
        contents = root.findall("Contents")
        if not contents:
            break

        for c in contents:
            key_el = c.find("Key")
            if key_el is not None and key_el.text:
                all_keys.append(key_el.text)

        is_truncated = root.find("IsTruncated")
        if is_truncated is not None and is_truncated.text == "true":
            marker_el = root.find("NextMarker")
            if marker_el is not None and marker_el.text:
                marker = marker_el.text
            else:
                break
        else:
            break

        print(f"  {page}:  {len(all_keys)} ...", flush=True)

    return all_keys


def main():
    prefix = "mall/products/"
    print(f" COS {prefix} ...", flush=True)
    keys = list_all_keys(prefix)
    total = len(keys)
    print(f" {total} ", flush=True)

    if total == 0:
        print("", flush=True)
        return

    
    print(f"\n {total} Ctrl+C ...", flush=True)
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        print("", flush=True)
        return

    deleted = 0
    failed = 0
    t0 = time.time()
    for i, key in enumerate(keys):
        url = f"https://{COS_ENDPOINT}/{quote(key, safe='/')}"
        headers = {"Host": COS_ENDPOINT}
        headers["Authorization"] = cos_sign("delete", f"/{key}")

        try:
            r = httpx.delete(url, headers=headers, timeout=15)
            if r.status_code in (200, 204):
                deleted += 1
            else:
                failed += 1
        except Exception:
            failed += 1

        if (i + 1) % 100 == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            eta = (total - i - 1) / rate
            print(f"  : {i+1}/{total} |  {deleted}  {failed} |  {rate:.0f}/s | ETA {eta:.0f}s", flush=True)

    elapsed = time.time() - t0
    print(f"\n! {elapsed:.1f}s", flush=True)
    print(f"  : {deleted}", flush=True)
    print(f"  : {failed}", flush=True)


if __name__ == "__main__":
    main()
