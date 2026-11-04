"""Validate the minimal website configuration using the official keyword parser."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import yaml
from trendradar.core.frequency import load_frequency_words

config = yaml.safe_load(Path('config/config.yaml').read_text(encoding='utf-8'))
assert config['report']['mode'] == 'current'
assert config['report']['display_mode'] == config['filter']['method'] == 'keyword'
for section in ['schedule', 'rss', 'notification', 'ai_analysis', 'ai_translation']:
    assert config[section]['enabled'] is False, section
assert config['storage']['backend'] == 'local'
assert config['storage']['formats']['html'] is True
assert config['storage']['pull']['enabled'] is False
assert config['display']['regions']['standalone'] is True
assert config['display']['regions']['hotlist'] is True
assert config['display']['standalone']['max_items'] == 0
assert set(config['display']['standalone']['platforms']) == {p['id'] for p in config['platforms']['sources']}
assert config['report']['max_news_per_keyword'] == 0
groups, _, _ = load_frequency_words('config/frequency_words.txt')
assert groups
workflow = yaml.safe_load(Path('.github/workflows/crawler.yml').read_text(encoding='utf-8'))
events = workflow.get('on', workflow.get(True))  # YAML 1.1 treats on as a boolean.
assert events['schedule'] == [{'cron': '0 0 * * *'}]
assert 'workflow_dispatch' in events
print(f'配置检查通过；{len(groups)} 个关键词组，全部平台独立展示')
