"""Run: python3 verify.py. Standard library only."""

from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re


def verify(root):
    root = root.resolve()
    count = 0
    for path in sorted(root.rglob('*')):
        if '.git' in path.relative_to(root).parts or not path.is_file():
            continue
        count += 1
        if path.suffix not in ('.md', '.json'):
            continue
        text = path.read_text(encoding='utf-8')
        assert not re.search(r'/Users/|/Applications/|vps_ovh_virginia|Lenovo IdeaPad Z580|/srv/fleet/', text), path
        if path.suffix == '.json':
            json.loads(text)
            continue
        for link in re.findall(r'\]\(([^)]+)\)', text):
            url = urlsplit(link)
            if url.scheme or url.netloc or not url.path:
                continue
            target = (path.parent / unquote(url.path)).resolve()
            assert target.is_relative_to(root), f'{path}: ссылка вне пакета: {link}'
            assert target.is_file(), f'{path}: файл отсутствует: {link}'
    agents = (root / 'AGENTS.md').read_text(encoding='utf-8')
    start = '<!-- engineering-discipline:start -->'
    end = '<!-- engineering-discipline:end -->'
    assert agents.count(start) == agents.count(end) == 1, 'Требуется один инженерный блок'
    assert agents.index(start) < agents.index(end), 'Неверный порядок границ блока'
    for name in ('architecture.md', 'runtime.md', 'verification.md', 'environment.md'):
        assert (root / 'docs' / 'engineering' / 'guidance' / name).is_file(), name
    print(f'OK: {count} файлов; локальные ссылки, переносимость, JSON и инженерный блок проверены.')


if __name__ == '__main__':
    verify(Path(__file__).resolve().parent)
