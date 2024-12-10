import yaml
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path
import re

class PromptManager:
    def __init__(self, templates_dir='docs'):
        self.templates_dir = Path(templates_dir)
        self.prompt_file = self.templates_dir / 'prompt_templates.yaml'
        self.document_file = self.templates_dir / 'document_templates.yaml'
        self.test_file = self.templates_dir / 'test_templates.yaml'
        self.history_dir = self.templates_dir / 'history'
        self.history_dir.mkdir(exist_ok=True)

    def load_templates(self, template_type='prompts'):
        """テンプレートファイルの読み込み"""
        templates = {}
        if template_type == 'prompts' and self.prompt_file.exists():
            with open(self.prompt_file, 'r', encoding='utf-8') as f:
                templates = yaml.safe_load(f)
        elif template_type == 'documents' and self.document_file.exists():
            with open(self.document_file, 'r', encoding='utf-8') as f:
                templates = yaml.safe_load(f)
        elif template_type == 'tests' and self.test_file.exists():
            with open(self.test_file, 'r', encoding='utf-8') as f:
                templates = yaml.safe_load(f)
        return templates

    def update_file_content(self, file_path, content):
        """ファイルの内容を更新"""
        try:
            file_path = Path(file_path)
            # ディレクトリが存在しない場合は作成
            if file_path.parent != Path('.'):
                file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # ファイルの内容を更新
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error updating {file_path}: {str(e)}")
            return False

    def sync_documents(self, template_name, lang=None):
        """ドキュメントの同期"""
        templates = self.load_templates('documents')
        if template_name not in templates:
            raise ValueError(f"Template {template_name} not found")

        template = templates[template_name]
        print(f"Syncing documents for template: {template_name}")
        print(f"Language: {lang if lang else 'all'}")
        
        # セクションごとの処理
        for section_name, section_data in template.get('sections', {}).items():
            # 言語別のテンプレートと対象ファイルを取得
            if lang:
                if lang not in section_data.get('template', {}):
                    print(f"Warning: No template found for language {lang} in section {section_name}")
                    continue
                
                template_content = section_data['template'][lang]
                target_files = section_data.get('files', {}).get(lang, [])
            else:
                # 言語指定がない場合は全ての言語を処理
                for current_lang, template_content in section_data.get('template', {}).items():
                    target_files = section_data.get('files', {}).get(current_lang, [])
                    
                    for target_file in target_files:
                        print(f"Processing {section_name} in {target_file}")
                        success = self.update_file_content(target_file, template_content)
                        if success:
                            print(f"Successfully updated {section_name} in {target_file}")
                        else:
                            print(f"Failed to update {section_name} in {target_file}")
                continue
            
            # 指定された言語のファイルを処理
            for target_file in target_files:
                print(f"Processing {section_name} in {target_file}")
                success = self.update_file_content(target_file, template_content)
                if success:
                    print(f"Successfully updated {section_name} in {target_file}")
                else:
                    print(f"Failed to update {section_name} in {target_file}")

    def generate_prompt(self, template_name, template_type='prompts', **kwargs):
        """プロンプトの生成"""
        templates = self.load_templates(template_type)
        if not templates or template_name not in templates:
            raise ValueError(f"Template {template_name} not found in {template_type}")
        
        template = templates[template_name]

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

def main():
    parser = argparse.ArgumentParser(description='Prompt Manager Tool')
    parser.add_argument('command', choices=['sync', 'generate'], help='Command to execute')
    parser.add_argument('template_name', help='Name of the template to use')
    parser.add_argument('--lang', choices=['en', 'ja'], help='Language filter for sync command')
    parser.add_argument('--type', choices=['prompts', 'documents', 'tests'], 
                      default='prompts', help='Template type')
    
    args = parser.parse_args()
    manager = PromptManager()

    try:
        if args.command == 'sync':
            manager.sync_documents(args.template_name, args.lang)
        elif args.command == 'generate':
            prompt = manager.generate_prompt(args.template_name, args.type)
            print(prompt)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
