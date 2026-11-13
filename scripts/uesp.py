"""UESP's MediaWiki API, shared by the fetch scripts. UESP's normal pages are blocked from cloud sessions;
the API is not."""
import json
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://en.uesp.net/w/api.php"
UA = "skyrim-build-tool/1.0 (static reference page; low request rate)"
BATCH = 50  # the API takes at most 50 titles per query


def get(**params):
    """One API call, as parsed JSON. Retries network trouble four times, then raises with the last error."""
    params["format"] = "json"
    url = API + "?" + urllib.parse.urlencode(params)
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.load(r)
            time.sleep(0.3)
            return data
        except (urllib.error.URLError, TimeoutError, ConnectionError, json.JSONDecodeError) as e:
            last = e
            time.sleep(2 ** (attempt + 1))
    raise RuntimeError(f"UESP API failed after 4 tries ({last!r}): {url}")


def batches(items, size=BATCH):
    items = list(items)
    return [items[i:i + size] for i in range(0, len(items), size)]


def page_text(page):
    """Wikitext of one page (action=parse)."""
    return get(action="parse", page=page, prop="wikitext")["parse"]["wikitext"]["*"]


def wikitext(titles, redirects=False):
    """Final page title -> wikitext for many pages. Missing pages are left out. With `redirects`, a title
    that redirects is returned under the page it lands on."""
    out = {}
    for batch in batches(titles):
        extra = {"redirects": 1} if redirects else {}
        d = get(action="query", prop="revisions", rvprop="content", rvslots="main", titles="|".join(batch), **extra)
        out.update({p["title"]: p["revisions"][0]["slots"]["main"]["*"]
                    for p in d["query"]["pages"].values() if "revisions" in p})
    return out
