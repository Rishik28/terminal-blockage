from pathlib import Path
from bs4 import BeautifulSoup
import base64, mimetypes, re
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
DIST = ROOT / 'dist'
DIST.mkdir(exist_ok=True)

def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
    return f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode('ascii')

html = (SRC / 'index.html').read_text(encoding='utf-8')
soup = BeautifulSoup(html, 'html.parser')
css = (SRC / 'css/style.css').read_text(encoding='utf-8')

def repl_url(match):
    raw = match.group(1).strip().strip('"\'')
    if raw.startswith(('data:', 'http:', 'https:', '#')):
        return match.group(0)
    path = SRC / raw
    if not path.exists():
        path = SRC / 'css' / raw
    if not path.exists():
        return match.group(0)
    return f'url("{data_uri(path)}")'

css = re.sub(r'url\(([^)]+)\)', repl_url, css)
link = soup.find('link', rel='stylesheet')
style = soup.new_tag('style')
style.string = css
if link:
    link.replace_with(style)
script = soup.find('script', src=True)
inline = soup.new_tag('script')
inline.string = (SRC / 'js/game.js').read_text(encoding='utf-8')
if script:
    script.replace_with(inline)
for img in soup.find_all('img', src=True):
    if img['src'].startswith('data:'):
        continue
    path = SRC / img['src']
    if path.exists():
        img['src'] = data_uri(path)
# Enemy portraits are swapped by JS; convert those source strings too.
js_text = inline.string
for portrait in [
    'enemy_goblin.png', 'enemy_slime.png', 'enemy_jester.png',
    'enemy_goblin_v2.png', 'enemy_slime_v2.png', 'enemy_jester_v2.png',
    'enemy_block_tyrant.png',
    'enemy_block_tyrant_v2.png',
    'enemy_chrome_strider_v3.png',
    'enemy_memory_pool_v3.png',
    'enemy_chaos_jester_v3.png',
    'enemy_monument_v3.png',
]:
    path = SRC / 'assets' / portrait
    js_text = js_text.replace(f"assets/{portrait}", data_uri(path))
for audio in ['knockout-bell.ogg']:
    path = SRC / 'assets' / 'audio' / audio
    js_text = js_text.replace(f"assets/audio/{audio}", data_uri(path))
inline.string = js_text
out = '<!doctype html>\n' + str(soup)
(DIST / 'index.html').write_text(out, encoding='utf-8')
print(DIST / 'index.html')
