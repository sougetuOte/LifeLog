from datetime import datetime
from typing import Dict, List, Tuple

class ValidationError(ValueError):
    """バリデーションエラー"""
    pass

class DataValidator:
    """テストデータバリデーションクラス"""

    # エラーメッセージ
    ERROR_MESSAGES = {
        'metadata_missing': 'メタデータが存在しません',
        'metadata_field_missing': 'メタデータに必須フィールドが存在しません: {}',
        'param_field_missing': 'パラメータに必須フィールドが存在しません: {}',
        'invalid_datetime': '無効な日時フォーマットです: {}',
        'entries_missing': 'エントリーデータが存在しません',
        'entry_field_missing': 'エントリーに必須フィールドが存在しません: {}',
        'invalid_user_id': '無効なユーザーID: {}',
        'invalid_date': '無効な日付フォーマットです: {} (YYYY/MM/DD形式で入力してください)',
        'empty_title': 'タイトルが空です',
        'empty_content': '内容が空です',
        'invalid_items_type': '活動項目はリスト形式である必要があります',
        'item_field_missing': '活動項目に必須フィールドが存在しません: {}',
        'empty_item_name': '活動項目名が空です',
        'empty_item_content': '活動項目の内容が空です',
        'date_range_invalid': '開始日は終了日以前である必要があります',
        'rate_type': '生成率は整数である必要があります',
        'rate_range': '生成率は1から100の間である必要があります',
        'items_type': '活動項目数は整数である必要があります',
        'items_range': '活動項目数は0以上である必要があります'
    }

    def __init__(self):
        self.valid_user_ids = ['admin', 'tetsu', 'gento']

    def validate_test_data(self, data: Dict) -> None:
        """テストデータ全体の検証"""
        # メタデータの検証
        if 'metadata' not in data:
            raise ValidationError(self.ERROR_MESSAGES['metadata_missing'])
        
        metadata = data['metadata']
        required_meta_fields = ['generated_at', 'parameters']
        for field in required_meta_fields:
            if field not in metadata:
                raise ValidationError(
                    self.ERROR_MESSAGES['metadata_field_missing'].format(field)
                )

        # パラメータの検証
        params = metadata['parameters']
        required_param_fields = ['start_date', 'end_date', 'rate', 'items_per_entry']
        for field in required_param_fields:
            if field not in params:
                raise ValidationError(
                    self.ERROR_MESSAGES['param_field_missing'].format(field)
                )

        # 生成日時の検証
        try:
            datetime.strptime(metadata['generated_at'], '%Y/%m/%d %H:%M:%S')
        except ValueError:
            raise ValidationError(
                self.ERROR_MESSAGES['invalid_datetime'].format(
                    metadata['generated_at']
                )
            )

        # エントリーの検証
        if 'entries' not in data:
            raise ValidationError(self.ERROR_MESSAGES['entries_missing'])
        
        for entry in data['entries']:
            self.validate_entry(entry)

    def validate_entry(self, entry: Dict) -> None:
        """個別エントリーの検証"""
        # 必須フィールドの確認
        required_fields = ['user_id', 'date', 'title', 'content', 'notes']
        for field in required_fields:
            if field not in entry:
                raise ValidationError(
                    self.ERROR_MESSAGES['entry_field_missing'].format(field)
                )

        # ユーザーIDの検証
        if entry['user_id'] not in self.valid_user_ids:
            raise ValidationError(
                self.ERROR_MESSAGES['invalid_user_id'].format(entry['user_id'])
            )

        # 日付の検証
        self.validate_date(entry['date'])

        # タイトルと内容の検証
        if not entry['title'].strip():
            raise ValidationError(self.ERROR_MESSAGES['empty_title'])
        if not entry['content'].strip():
            raise ValidationError(self.ERROR_MESSAGES['empty_content'])

        # 活動項目の検証
        if 'items' in entry:
            if not isinstance(entry['items'], list):
                raise ValidationError(self.ERROR_MESSAGES['invalid_items_type'])
            
            for item in entry['items']:
                self.validate_diary_item(item)

    def validate_diary_item(self, item: Dict) -> None:
        """活動項目の検証"""
        required_fields = ['item_name', 'item_content']
        for field in required_fields:
            if field not in item:
                raise ValidationError(
                    self.ERROR_MESSAGES['item_field_missing'].format(field)
                )

        if not item['item_name'].strip():
            raise ValidationError(self.ERROR_MESSAGES['empty_item_name'])
        if not item['item_content'].strip():
            raise ValidationError(self.ERROR_MESSAGES['empty_item_content'])

    def validate_date(self, date_str: str) -> datetime:
        """日付文字列の検証"""
        try:
            return datetime.strptime(date_str, '%Y/%m/%d')
        except ValueError:
            raise ValidationError(
                self.ERROR_MESSAGES['invalid_date'].format(date_str)
            )

    def validate_date_range(self, start_date: str, end_date: str) -> Tuple[datetime, datetime]:
        """日付範囲の検証"""
        start = self.validate_date(start_date)
        end = self.validate_date(end_date)
        
        if start > end:
            raise ValidationError(self.ERROR_MESSAGES['date_range_invalid'])
        
        return start, end

    def validate_rate(self, rate: int) -> None:
        """生成率の検証"""
        if not isinstance(rate, int):
            raise ValidationError(self.ERROR_MESSAGES['rate_type'])
        if not 1 <= rate <= 100:
            raise ValidationError(self.ERROR_MESSAGES['rate_range'])

    def validate_items_per_entry(self, items: int) -> None:
        """活動項目数の検証"""
        if not isinstance(items, int):
            raise ValidationError(self.ERROR_MESSAGES['items_type'])
        if items < 0:
            raise ValidationError(self.ERROR_MESSAGES['items_range'])
