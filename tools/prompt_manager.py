import yaml
import sys
import os
from datetime import datetime
from pathlib import Path

class PromptManager:
    def __init__(self, templates_dir='docs'):
        self.templates_dir = Path(templates_dir)
        self.prompt_file = self.templates_dir / 'prompt_templates.yaml'
        self.test_file = self.templates_dir / 'test_templates.yaml'
        self.history_dir = self.templates_dir / 'history'
        self.history_dir.mkdir(exist_ok=True)

    def load_templates(self):
        """テンプレートファイルの読み込み"""
        templates = {}
        if self.prompt_file.exists():
            with open(self.prompt_file, 'r', encoding='utf-8') as f:
                templates['prompts'] = yaml.safe_load(f)
        if self.test_file.exists():
            with open(self.test_file, 'r', encoding='utf-8') as f:
                templates['tests'] = yaml.safe_load(f)
        return templates

    def save_template(self, template_type, content):
        """テンプレートの保存"""
        target_file = self.prompt_file if template_type == 'prompts' else self.test_file
        with open(target_file, 'w', encoding='utf-8') as f:
            yaml.dump(content, f, allow_unicode=True, sort_keys=False)

    def backup_template(self, template_type):
        """テンプレートのバックアップ"""
        source = self.prompt_file if template_type == 'prompts' else self.test_file
        if source.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.history_dir / f'{source.stem}_{timestamp}.yaml'
            with open(source, 'r', encoding='utf-8') as src, \
                 open(backup_file, 'w', encoding='utf-8') as dst:
                dst.write(src.read())

    def generate_prompt(self, template_name, template_type='prompts', **kwargs):
        """プロンプトの生成"""
        templates = self.load_templates()
        if template_type not in templates:
            raise ValueError(f"Template type {template_type} not found")
        
        template = templates[template_type].get(template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found")

        # テンプレートの展開
        prompt = f"Task: {template['task']}\n\n"
        
        if 'target_files' in template:
            prompt += "Target Files:\n"
            for file in template['target_files']:
                prompt += f"- {file}\n"
        
        if 'section' in template:
            prompt += f"\nSection: {template['section']}\n"
        
        if 'template' in template:
            prompt += f"\nTemplate:\n{template['template']}\n"
        
        if 'notes' in template:
            prompt += f"\nNotes:\n{template['notes']}\n"

        return prompt

    def update_template(self, template_type, template_name, updates):
        """テンプレートの更新"""
        templates = self.load_templates()
        if template_type not in templates:
            raise ValueError(f"Template type {template_type} not found")
        
        if template_name not in templates[template_type]:
            raise ValueError(f"Template {template_name} not found")

        # バックアップの作成
        self.backup_template(template_type)

        # テンプレートの更新
        templates[template_type][template_name].update(updates)
        self.save_template(template_type, templates[template_type])

    def execute_prompt(self, prompt):
        """プロンプトの実行（実装例）"""
        print("Generated Prompt:")
        print("-" * 50)
        print(prompt)
        print("-" * 50)
        # ここに実際の実行ロジックを実装
        # 例：OpenAI APIの呼び出しなど

def main():
    manager = PromptManager()
    
    # コマンドライン引数の解析
    if len(sys.argv) < 3:
        print("Usage: python prompt_manager.py <template_type> <template_name>")
        sys.exit(1)

    template_type = sys.argv[1]
    template_name = sys.argv[2]

    try:
        # プロンプトの生成と実行
        prompt = manager.generate_prompt(template_name, template_type)
        manager.execute_prompt(prompt)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
