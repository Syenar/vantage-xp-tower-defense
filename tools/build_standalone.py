from pathlib import Path
import base64, mimetypes, re
ROOT=Path(__file__).resolve().parents[1]
src=ROOT/'index.html'
out=ROOT/'Vantage_XP_Tower_Defense_PLAYABLE.html'
text=src.read_text(encoding='utf-8')
# A standalone file cannot install as a PWA; strip the external manifest reference.
text=re.sub(r'<link\s+rel=["\']manifest["\']\s+href=["\'][^"\']+["\']\s*/?>','',text,flags=re.I)

def data_uri(path: Path)->str:
    mime=mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
    return f"data:{mime};base64,"+base64.b64encode(path.read_bytes()).decode('ascii')

# Replace all direct asset references in HTML/CSS/JS.
refs=sorted(set(re.findall(r"assets/[A-Za-z0-9_./-]+\.(?:png|jpg|jpeg|webp)",text)), key=len, reverse=True)
for ref in refs:
    p=ROOT/ref
    if not p.exists():
        raise SystemExit(f'Missing referenced asset: {ref}')
    text=text.replace(ref,data_uri(p))

# Replace dynamic map filenames with embedded data URIs only inside MAP_ASSETS.
m=re.search(r"const MAP_ASSETS=\[(.*?)\];",text,re.S)
if not m:
    raise SystemExit('MAP_ASSETS not found')
block=m.group(1)
for name in re.findall(r"['\"]([^'\"]+\.(?:png|jpg|jpeg|webp))['\"]",block):
    p=ROOT/'assets/maps'/name
    if not p.exists():
        raise SystemExit(f'Missing map asset: {p}')
    block=block.replace(repr(name),repr(data_uri(p))).replace('"'+name+'"','"'+data_uri(p)+'"')
text=text[:m.start(1)]+block+text[m.end(1):]
out.write_text(text,encoding='utf-8')
print(out)
print(f'{out.stat().st_size/1024/1024:.1f} MiB')
print('remaining asset refs:',len(re.findall(r"assets/[A-Za-z0-9_./-]+\.(?:png|jpg|jpeg|webp)",text)))
