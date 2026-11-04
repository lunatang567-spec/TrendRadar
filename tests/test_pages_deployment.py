"""Exercise official HTML generation and the deployment boundary without network."""
import os
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest

from scripts.prepare_pages import prepare
from trendradar.report.generator import generate_html_report
from trendradar.report.html import render_html_content


class PagesDeploymentTests(unittest.TestCase):
    def test_official_report_keeps_unmatched_full_list_and_only_stages_html(self):
        with tempfile.TemporaryDirectory() as directory:
            previous = Path.cwd()
            try:
                os.chdir(directory)
                standalone = {'platforms': [{'id': 'baidu', 'name': '百度热搜', 'items': [
                    {'title': '未命中关键词的标题', 'url': 'https://www.baidu.com/news', 'rank': 1, 'ranks': [1]}
                ]}], 'rss_feeds': []}
                generate_html_report([], 1, mode='current', date_folder='test', time_filename='0800',
                    render_html_func=lambda data, total, mode, update: render_html_content(
                        data, total, mode, update, standalone_data=standalone))
                with closing(sqlite3.connect('output/news.db')) as conn:
                    conn.execute('CREATE TABLE news_items (title TEXT)')
                    conn.execute("INSERT INTO news_items VALUES ('未命中关键词的标题')")
                    conn.commit()
                prepare()
                html = Path('cloudflare_dist/index.html').read_text(encoding='utf-8')
                self.assertIn('未命中关键词的标题', html)
                self.assertIn('href="https://www.baidu.com/news"', html)
                self.assertEqual([p.name for p in Path('cloudflare_dist').iterdir()], ['index.html'])
            finally:
                os.chdir(previous)

    def test_rejects_existing_homepage_without_new_report(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, 'index.html').write_text('<html>old</html>', encoding='utf-8')
            with self.assertRaisesRegex(RuntimeError, '本次采集未生成'):
                prepare(Path(directory))

    def test_rejects_empty_crawl(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'output').mkdir()
            for path in [root / 'index.html', root / 'output/index.html']:
                path.write_text('<html>empty</html>', encoding='utf-8')
            with self.assertRaisesRegex(RuntimeError, '没有成功采集'):
                prepare(root)
