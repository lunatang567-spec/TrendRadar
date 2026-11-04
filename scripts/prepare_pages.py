"""Validate this run's official report and stage only the public homepage."""
from html.parser import HTMLParser
from contextlib import closing
from pathlib import Path
import shutil
import sqlite3


class NewsLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and 'news-link' in attrs.get('class', '').split():
            if attrs.get('href', '').startswith('https://'):
                self.count += 1


def prepare(root=Path('.')):
    root = Path(root)
    index = root / 'index.html'
    generated = root / 'output/index.html'
    if not index.is_file() or not generated.is_file():
        raise RuntimeError('本次采集未生成首页，拒绝部署旧文件')
    if index.read_bytes() != generated.read_bytes():
        raise RuntimeError('首页与本次 output/index.html 不一致')
    total = 0
    for db in (root / 'output').rglob('*.db'):
        with closing(sqlite3.connect(f'{db.resolve().as_uri()}?mode=ro', uri=True)) as connection:
            tables = {r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if 'news_items' in tables:
                total += connection.execute('SELECT COUNT(*) FROM news_items').fetchone()[0]
    if total == 0:
        raise RuntimeError('没有成功采集到新闻，拒绝发布空报告')
    html = index.read_text(encoding='utf-8')
    parser = NewsLinks()
    parser.feed(html)
    if parser.count == 0 or 'standalone-group' not in html or 'name="viewport"' not in html:
        raise RuntimeError('报告缺少新闻链接、独立展示区或移动端 viewport')
    dist = root / 'cloudflare_dist'
    if dist.exists():
        shutil.rmtree(dist)
    dist.mkdir()
    shutil.copyfile(index, dist / 'index.html')
    print(f'已验证 {total} 条新闻、{parser.count} 个新闻链接；仅打包 index.html')


if __name__ == '__main__':
    prepare()
