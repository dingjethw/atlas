import json, os
D = r"D:\w3c\Hackthon\task1"
data = open(os.path.join(D, "coverage.json"), encoding="utf8").read()
tpl = open(os.path.join(D, "atlas.template.html"), encoding="utf8").read()
out = tpl.replace("/*__DATA__*/", data)
assert out.count("/*__DATA__*/") == 0
open(os.path.join(D, "atlas.html"), "w", encoding="utf8").write(out)
print("atlas.html %.0f KB" % (len(out.encode()) / 1024))
