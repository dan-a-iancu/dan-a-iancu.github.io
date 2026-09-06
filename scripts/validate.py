#!/usr/bin/env python3
"""Static checks for the site. Catches failure modes a Hugo build reports late,
confusingly, or not at all. Stdlib only. Exit 1 on any failure.

Run before every commit (see AGENTS.md "Before you commit").
"""
import os, re, sys, glob, datetime

CONTENT="content"; FAIL=[]; WARN=[]
def fail(m): FAIL.append(m)
def warn(m): WARN.append(m)

def front_matter(p):
    s=open(p, encoding="utf-8").read()
    if not s.startswith("---"): return None, s
    parts=s.split("\n---\n", 1)
    if len(parts)!=2: return None, s
    return parts[0][4:], parts[1]

pages=[p for p in glob.glob(f"{CONTENT}/**/*.md", recursive=True)]

# ---- 1. filter-referent existence (the G1 build breaker) ---------------------
declared=set()
for p in pages:
    fm,_=front_matter(p)
    if not fm: continue
    m=re.search(r'^publication_types:\s*\[(.*?)\]', fm, re.M)
    if m: declared |= {t.strip().strip('"\'') for t in m.group(1).split(",") if t.strip()}
    for m in re.finditer(r'^publication_types:\s*\n((?:\s*-\s*.+\n)+)', fm, re.M):
        declared |= {l.strip().lstrip("-").strip().strip('"\'') for l in m.group(1).splitlines()}

for p in pages:
    s=open(p, encoding="utf-8").read()
    for ref in re.findall(r'publication_type:\s*"?([\w-]+)"?', s):
        if ref not in declared:
            fail(f"G1 nil-deref risk: {p} filters publication_type '{ref}' which NO page declares")
    for ref in re.findall(r'^\s*tag:\s*"?([\w -]+)"?', s, re.M):
        tags=set()
        for q in pages:
            fmq,_=front_matter(q)
            if fmq: tags |= set(re.findall(r'^\s*-\s*(.+)$', fmq, re.M))
        if ref not in {t.strip().strip('"\'') for t in tags}:
            fail(f"G1 nil-deref risk: {p} filters tag '{ref}' which no page declares")
    for ref in re.findall(r'folders:\s*\[(.*?)\]', s):
        for f in [x.strip().strip('"\'') for x in ref.split(",") if x.strip()]:
            if not os.path.isdir(os.path.join(CONTENT, f)):
                fail(f"G1: {p} filters folders ['{f}'] but content/{f}/ does not exist")

# ---- 2. no future dates (buildFuture is false in production) ----------------
today=datetime.date.today().isoformat()
for p in pages:
    fm,_=front_matter(p)
    if not fm: continue
    for k in ("date","publishDate"):
        m=re.search(rf'^{k}:\s*(\d{{4}}-\d{{2}}-\d{{2}})', fm, re.M)
        if m and m.group(1) > today:
            fail(f"future {k} {m.group(1)} in {p} -- page will silently vanish in production")

# ---- 3. local link / resource existence -------------------------------------
for p in pages:
    fm, body = front_matter(p)
    d=os.path.dirname(p)
    targets=[]
    if fm: targets += [(u.strip('\'"'),"links[].url")
                       for u in re.findall(r'^\s*url:\s*(\S+)', fm, re.M)]
    targets += [(u,"markdown") for u in re.findall(r'\]\(([^)\s#]+)\)', body or "")]
    for url, where in targets:
        if url.startswith(("http://","https://","mailto:","/uploads/","#")): continue
        if url.startswith("/"): continue
        cands=[os.path.join(d,url), os.path.join(d,os.path.basename(url)),
               os.path.join("assets/media",url), os.path.join("static",url.lstrip("/"))]
        if not any(os.path.exists(c) for c in cands):
            fail(f"broken {where} in {p}: '{url}'")

# ---- 4. enum validation ------------------------------------------------------
CSL={"article-journal","paper-conference","chapter","book","thesis","manuscript",
     "report","article","speech","patent"}
LINKS={"pdf","preprint","doi","code","dataset","model","slides","video","poster","project",
       "site","source","bibtex","canonical","crosspost","discussion","event","calendar",
       "registration","demo"}
for p in pages:
    fm,_=front_matter(p)
    if not fm: continue
    for m in re.finditer(r'publication_types:\s*\[(.*?)\]', fm):
        for t in [x.strip().strip('"\'') for x in m.group(1).split(",") if x.strip()]:
            if t not in CSL: fail(f"invalid publication_type '{t}' in {p}")
    for t in re.findall(r'^\s*-\s*type:\s*(\S+)', fm, re.M):
        if t not in LINKS: fail(f"unregistered link type '{t}' in {p}")

# ---- 5. deprecated fields ----------------------------------------------------
for p in pages:
    fm,_=front_matter(p)
    if not fm: continue
    for pat,msg in [(r'^doi:', "top-level doi: (use hugoblox.ids.doi)"),
                    (r'^url_\w+:', "url_* field"),
                    (r'^external_link:', "external_link"),
                    (r'view:\s*compact', "view: compact does not exist (G2)"),
                    (r'show_(authors|buttons|description|awards):', "inert show_* key (G3)")]:
        if re.search(pat, fm, re.M): fail(f"deprecated/inert in {p}: {msg}")

# ---- 6. asset size gate ------------------------------------------------------
for root,_,files in os.walk(CONTENT):
    for f in files:
        fp=os.path.join(root,f); sz=os.path.getsize(fp)
        if sz > 5*1024*1024: fail(f"asset over 5 MB: {fp} ({sz/1048576:.1f} MB)")
        elif sz > 3*1024*1024: warn(f"large asset: {fp} ({sz/1048576:.1f} MB)")

# ---- 7. baseURL sanity -------------------------------------------------------
cfg=open("config/_default/hugo.yaml", encoding="utf-8").read()
m=re.search(r'^baseURL:\s*[\'"]?([^\'"\n]+)', cfg, re.M)
if not m or not m.group(1).startswith(("http://","https://")):
    fail("baseURL has no scheme -- Hugo will treat it as a path")

print(f"checked {len(pages)} content files")
for w in WARN: print(f"  WARN  {w}")
for f in FAIL: print(f"  FAIL  {f}")
print(f"\n{len(FAIL)} failures, {len(WARN)} warnings")
sys.exit(1 if FAIL else 0)
