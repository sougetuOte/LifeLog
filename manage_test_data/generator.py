import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class GeneratorError(Exception):
    """ジェネレーターエラー"""
    pass

class TestDataGenerator:
    """テストデータ生成クラス"""

    # 有効なユーザーID
    VALID_USER_IDS = ['admin', 'tetsu', 'gento']

    # 必須テンプレート
    REQUIRED_TEMPLATES = {
        'titles': list,
        'contents': list,
        'notes': {
            'weather': list,
            'feeling': list
        },
        'items': list
    }

    # 活動項目の詳細テンプレート
    ITEM_CONTENT_TEMPLATES = [
        '{item}を{duration}分行いました。{result}',
        '{item}に取り組みました。{impression}',
        '{item}の時間を設けました。{comment}'
    ]

    # 活動結果のバリエーション
    ITEM_RESULTS = [
        '良い運動になりました',
        '集中して取り組めました',
        '充実した時間でした',
        'とても楽しかったです',
        '良い気分転換になりました'
    ]

    # 活動の印象
    ITEM_IMPRESSIONS = [
        'とても有意義でした',
        '新しい発見がありました',
        '良い経験になりました',
        '次回も続けたいです',
        'もっと深めていきたいです'
    ]

    # 活動コメント
    ITEM_COMMENTS = [
        '継続は力なりを実感しました',
        '日々の積み重ねが大切だと感じました',
        '良い習慣になってきました',
        '今後も続けていきたいです',
        '少しずつ上達を感じます'
    ]

    def __init__(self, templates: Dict):
        self.validate_templates(templates)
        self.templates = templates

    def validate_templates(self, templates: Dict) -> None:
        """テンプレート構造の検証"""
        def validate_structure(template: Dict, required: Dict, path: str = '') -> None:
            for key, expected_type in required.items():
                current_path = f'{path}.{key}' if path else key
                
                if key not in template:
                    raise GeneratorError(f'必須テンプレートが存在しません: {current_path}')
                
                if isinstance(expected_type, dict):
                    if not isinstance(template[key], dict):
                        raise GeneratorError(
                            f'無効なテンプレート型: {current_path} '
                            f'(expected dict, got {type(template[key]).__name__})'
                        )
                    validate_structure(template[key], expected_type, current_path)
                else:
                    if not isinstance(template[key], expected_type):
                        raise GeneratorError(
                            f'無効なテンプレート型: {current_path} '
                            f'(expected {expected_type.__name__}, '
                            f'got {type(template[key]).__name__})'
                        )
                    if not template[key]:  # リストが空でないことを確認
                        raise GeneratorError(f'テンプレートが空です: {current_path}')

        validate_structure(templates, self.REQUIRED_TEMPLATES)

    def generate_entries(self, start_date: datetime, end_date: datetime, 
                        rate: int = 100, items_per_entry: int = 3) -> List[Dict]:
        """指定された期間のエントリーを生成"""
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise GeneratorError('開始日と終了日はdatetimeオブジェクトである必要があります')
        
        if start_date > end_date:
            raise GeneratorError('開始日は終了日以前である必要があります')

        if not 1 <= rate <= 100:
            raise GeneratorError('生成率は1から100の間である必要があります')

        if items_per_entry < 0:
            raise GeneratorError('活動項目数は0以上である必要があります')

        entries = []
        date_range = (end_date - start_date).days + 1

        # 各日付について
        for day in range(date_range):
            current_date = start_date + timedelta(days=day)
            
            # 各ユーザーについて
            for user in self.VALID_USER_IDS:
                # 生成率に基づいてエントリーを生成するかどうかを決定
                if random.randint(1, 100) <= rate:
                    entry = self._generate_entry(user, current_date, items_per_entry)
                    entries.append(entry)

        return entries

    def _generate_entry(self, user_id: str, date: datetime, items_per_entry: int) -> Dict:
        """1つのエントリーを生成"""
        # 天気と気分をランダムに選択
        weather = random.choice(self.templates['notes']['weather'])
        feeling = random.choice(self.templates['notes']['feeling'])

        # タイトルテンプレートをランダムに選択して適用
        title_template = random.choice(self.templates['titles'])
        title = title_template.format(
            date=date.strftime('%Y/%m/%d'),
            weather=weather
        )

        # 内容テンプレートをランダムに選択して適用
        content_template = random.choice(self.templates['contents'])
        activity = random.choice(self.templates['items'])
        content = content_template.format(
            activity=activity,
            feeling=feeling
        )

        # 活動項目を生成
        items_count = random.randint(0, items_per_entry)
        items = []
        available_items = list(self.templates['items'])
        
        for _ in range(items_count):
            if not available_items:
                break
                
            item_name = random.choice(available_items)
            available_items.remove(item_name)  # 同じ項目を重複して使用しない
            
            # 詳細な内容を生成
            content_template = random.choice(self.ITEM_CONTENT_TEMPLATES)
            item_content = content_template.format(
                item=item_name,
                duration=random.randint(15, 120),
                result=random.choice(self.ITEM_RESULTS),
                impression=random.choice(self.ITEM_IMPRESSIONS),
                comment=random.choice(self.ITEM_COMMENTS)
            )

            items.append({
                'item_name': item_name,
                'item_content': item_content
            })

        # メモを生成
        notes = f'天気: {weather}\n気分: {feeling}'

        return {
            'user_id': user_id,
            'date': date.strftime('%Y/%m/%d'),
            'title': title,
            'content': content,
            'notes': notes,
            'items': items
        }
