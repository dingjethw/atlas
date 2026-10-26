# The Unfinished Web — TPAC 2026 hackathon, challenge 01 (visualize standards data)

One file. Open `atlas.html` in any browser, no server, no network.

It joins two public datasets nobody joins:

- **w3c/webref** ED crawl → every API member (attribute / method / constant) declared in the
  WebIDL of 354 IDL files, plus each spec's title and URL.
- **MDN browser-compat-data** → whether desktop Chrome, Safari and Firefox ship each member
  by default (flagged / preview-only counts as not shipped).

Result: for every spec, how much of its declared surface is actually shippable, and by how many
of the three engines.

## The four numbers (generated, not hand-written)

| | |
|---|---|
| 4,964 | API members scored (of 8,194 declared in 1,188 interfaces / 354 IDL files) |
| 67.1% | shipped by all three engines |
| 954 | shipped by exactly one engine — Chrome 857, Safari 54, Firefox 43 |
| 220 | documented in BCD but shipped by no engine by default |

Ranked by members missing from 2+ engines, the top of the table is WebNN (115 members, 0% everywhere),
WebXR (73), WebUSB (65), WebXR Layers (56), then HTML (45) and Web Bluetooth (45). HTML is also the
counter-example: 983 members, 91% in all three.

Second finding, in the subtitle: of 1,188 interfaces that webref extracts from spec text, only 885
have any MDN compat record. The platform's own machine-readable inventory is 25% incomplete —
that is a W3C-tooling gap, not a browser gap.

## 60-second demo script

1. "This bar is the whole Web platform's IDL surface: 4,964 members. A third of it is not uniformly shipped."
2. "Two thirds works everywhere. 954 members work in exactly one engine — and it's almost all one vendor: 857 Chrome-only."
3. "Here's the ranking a spec editor wants: WebNN, 115 members, shipped by nobody by default. WebXR, 73, Chrome only. These are the specs where interop tests would buy the most."
4. "Click any spec: the exact members that ship once or never. Both inputs are public, so anyone can re-run this on their own spec set."

## Rebuild

```
python fetch.py     # webref tarball + BCD bundle -> data/   (~50 MB, needs network)
python compute.py   # join + self-checks -> coverage.json
python build.py     # inline JSON -> atlas.html
```
`compute.py` and `atlas.html` assert their own invariants (bucket sums, row count, drawer opens);
a page that fails prints `SELFTEST FAIL` in the title.

## Limits, stated on the page too

- Scored only where BCD documents the member — absent BCD records are not "unimplemented", just unmeasured.
- Measures documented availability, not conformance to spec prose.
- IDL only: no CSS properties, HTTP headers, HTML elements.
- Vendors = desktop Chrome / Safari / Firefox; no mobile, no other engines.
