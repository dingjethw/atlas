import urllib.request, tarfile, json, os, sys, io, time

D = r"D:\w3c\Hackthon\task1\data"
os.makedirs(D, exist_ok=True)

def dl(url, path, timeout=180):
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        print("cached", path); return path
    t = time.time()
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'tpac-hack'}), timeout=timeout) as r, open(path, 'wb') as f:
        while True:
            c = r.read(1 << 16)
            if not c: break
            f.write(c)
    print("got", url, os.path.getsize(path), "%.0fs" % (time.time() - t))
    return path

tar = dl("https://codeload.github.com/w3c/webref/tar.gz/refs/heads/main", D + r"\webref.tgz")
bcd = dl("https://cdn.jsdelivr.net/npm/@mdn/browser-compat-data/data.json", D + r"\bcd.json")

with tarfile.open(tar) as t:
    names = [n for n in t.getnames() if "/ed/idl/" in n or "/ed/headings/" in n]
    print("members", len(names))
    t.extractall(D + r"\webref", members=[m for m in t.getmembers() if m.name in names])
print("DONE", len(os.listdir(D + r"\webref")))
