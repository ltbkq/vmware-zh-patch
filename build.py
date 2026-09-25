#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate vmware.vmsg from zh/*.tsv translation tables.

Rules (empirically verified against the real VMware message loader):
  * first line: .encoding = "UTF-8"
  * entries:    msg.xxx = "value"
  * the only escape mechanism is |XX  (hex byte): |22 -> ", |7C -> |, |0A -> newline
  * backslash is NOT special (a literal \n in the value is displayed as-is)
  * an unescaped " or | kills the whole dictionary (DictionaryParseReadLine syntax error)
"""
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.abspath(__file__))
TSV_DIR = os.path.join(ROOT, "zh")
OUT = os.path.join(ROOT, "vmware.vmsg")
STRINGS = os.path.join(ROOT, "strings.json")

# format specifiers we must preserve exactly
FMT = re.compile(
    r"%(?:\d+\$)?[-+ #0]*(?:\d+|\*)?(?:\.(?:\d+|\*))?"
    r"(?:hh|h|ll|l|j|z|t|L)?[diouxXeEfFgGaAcspn%]"
    r"|%\[\^?[^\]]*\]"
    r"|<[a-zA-Z][a-zA-Z0-9_]*>"
)
# GTK mnemonics: _x  (x must be a letter/digit, not an underscore)
MNEMONIC = re.compile(r"(?<!_)_(?=[A-Za-z0-9])")


def unescape_tsv(v: str) -> str:
    """TSV values are single-line; \\n means newline, \\\\ means backslash."""
    out, i = [], 0
    while i < len(v):
        if v[i] == "\\" and i + 1 < len(v):
            n = v[i + 1]
            if n == "n":
                out.append("\n")
                i += 2
                continue
            if n == "\\":
                out.append("\\")
                i += 2
                continue
        out.append(v[i])
        i += 1
    return "".join(out)


def escape(v: str) -> str:
    """Encode a raw string for the .vmsg value grammar."""
    r = []
    for ch in v:
        if ch == "|":
            r.append("|7C")
        elif ch == '"':
            r.append("|22")
        elif ch == "\n":
            r.append("|0A")
        elif ch == "\r":
            r.append("|0D")
        elif ch == "\t":
            r.append("|09")
        else:
            r.append(ch)
    return "".join(r)


def fmt_set(s: str):
    return sorted(FMT.findall(s))


def mnemonic_set(s: str):
    return sorted(m.group(0).lower() for m in MNEMONIC.finditer(s))


def load_sources():
    if not os.path.exists(STRINGS):
        sys.exit("missing %s" % STRINGS)
    data = json.load(open(STRINGS, encoding="utf-8"))
    return data["entries"], data["order"]


def load_translations():
    entries, order = {}, []
    files = sorted(f for f in os.listdir(TSV_DIR) if f.endswith(".tsv"))
    for fn in files:
        path = os.path.join(TSV_DIR, fn)
        cur = None
        for lineno, raw in enumerate(open(path, encoding="utf-8"), 1):
            line = raw.rstrip("\n")
            if not line:
                continue
            if "\t" in line:
                key, val = line.split("\t", 1)
                if key in entries:
                    sys.exit("%s:%d duplicate key %s" % (fn, lineno, key))
                cur = key
                entries[key] = unescape_tsv(val)
                order.append(key)
            else:
                if cur is None:
                    sys.exit("%s:%d orphan continuation" % (fn, lineno))
                entries[cur] += "\n" + line
    return entries, order, files


def main():
    src, src_order = load_sources()
    tr, tr_order, files = load_translations()

    unknown = [k for k in tr_order if k not in src]
    fmt_bad, mnem_warn = [], []
    for k, v in tr.items():
        if k not in src:
            continue
        en = src[k]
        if fmt_set(en) != fmt_set(v):
            fmt_bad.append((k, fmt_set(en), fmt_set(v)))
        # a literal % that is not a specifier is fine only when English does it too
        en_stray = len(FMT.sub("", en)) - len(FMT.sub("", en).replace("%", ""))
        zh_stray = len(FMT.sub("", v)) - len(FMT.sub("", v).replace("%", ""))
        if zh_stray > en_stray:
            fmt_bad.append((k, "extra %% (en has %d)" % en_stray, v))

    if unknown:
        print("!! keys not present in strings.json (%d):" % len(unknown))
        for k in unknown:
            print("   ", k)
    if fmt_bad:
        print("!! format specifier mismatches (%d):" % len(fmt_bad))
        for k, a, b in fmt_bad:
            print("   %-70s en=%s zh=%s" % (k, a, b))
    if unknown or fmt_bad:
        sys.exit(1)

    # emit, in source order first (unknown-to-source keys never happen now)
    keys = [k for k in src_order if k in tr]
    with open(OUT, "w", encoding="utf-8") as f:
        f.write('.encoding = "UTF-8"\n')
        for k in keys:
            f.write('%s = "%s"\n' % (k, escape(tr[k])))

    print("files   : %s" % ", ".join(files))
    print("entries : %d / %d translated" % (len(keys), len(src)))
    print("output  : %s" % OUT)


if __name__ == "__main__":
    main()
