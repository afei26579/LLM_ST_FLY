"""
检查和修复响应格式的管理命令
"""
from django.core.management.base import BaseCommand
from django.apps import apps
from django.conf import settings
import os
import ast
import re
from typing import List, Dict, Any


class Command(BaseCommand):
    help = '检查项目中的响应格式是否符合统一标准'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='自动修复发现的问题',
        )
        parser.add_argument(
            '--app',
            type=str,
            help='只检查指定的应用',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='显示详细信息',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始检查响应格式...'))
        
        issues = []
        
        # 获取要检查的应用
        if options['app']:
            apps_to_check = [options['app']]
        else:
            apps_to_check = [app.name for app in apps.get_app_configs() 
                           if not app.name.startswith('django.')]
        
        for app_name in apps_to_check:
            if options['verbose']:
                self.stdout.write(f'检查应用: {app_name}')
            
            app_issues = self.check_app_views(app_name, options['verbose'])
            issues.extend(app_issues)
        
        # 显示检查结果
        self.display_results(issues)
        
        # 如果需要修复
        if options['fix'] and issues:
            self.fix_issues(issues)
    
    def check_app_views(self, app_name: str, verbose: bool = False) -> List[Dict[str, Any]]:
        """检查应用的视图文件"""
        issues = []
        
        try:
            app_config = apps.get_app_config(app_name)
            app_path = app_config.path
            views_file = os.path.join(app_path, 'views.py')
            
            if not os.path.exists(views_file):
                if verbose:
                    self.stdout.write(f'  跳过 {app_name}: 没有views.py文件')
                return issues
            
            with open(views_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否导入了StandardResponse
            if 'from core.response import StandardResponse' not in content:
                issues.append({
                    'type': 'missing_import',
                    'file': views_file,
                    'message': '缺少StandardResponse导入',
                    'severity': 'warning'
                })
            
            # 检查是否还在使用旧的Response格式
            old_response_patterns = [
                r'return Response\(\s*\{[^}]*["\']code["\']',
                r'return JsonResponse\(\s*\{[^}]*["\']code["\']',
                r'Response\(\s*\{[^}]*["\']message["\']',
                r'JsonResponse\(\s*\{[^}]*["\']message["\']'
            ]
            
            for pattern in old_response_patterns:
                matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        'type': 'old_response_format',
                        'file': views_file,
                        'line': line_num,
                        'message': '发现旧的响应格式，建议使用StandardResponse',
                        'severity': 'error',
                        'match': match.group()
                    })
            
            # 检查是否使用了标准化视图基类
            if 'class' in content and 'ViewSet' in content:
                if 'StandardModelViewSet' not in content and 'from core.views import' not in content:
                    issues.append({
                        'type': 'missing_standard_viewset',
                        'file': views_file,
                        'message': '建议使用StandardModelViewSet基类',
                        'severity': 'info'
                    })
            
            if verbose:
                self.stdout.write(f'  检查完成 {app_name}: 发现 {len([i for i in issues if i["file"] == views_file])} 个问题')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'检查应用 {app_name} 时出错: {str(e)}')
            )
        
        return issues
    
    def display_results(self, issues: List[Dict[str, Any]]):
        """显示检查结果"""
        if not issues:
            self.stdout.write(self.style.SUCCESS('✅ 没有发现问题，所有响应格式都符合标准！'))
            return
        
        # 按严重程度分组
        errors = [i for i in issues if i['severity'] == 'error']
        warnings = [i for i in issues if i['severity'] == 'warning']
        infos = [i for i in issues if i['severity'] == 'info']
        
        self.stdout.write(f'\n发现 {len(issues)} 个问题:')
        
        if errors:
            self.stdout.write(self.style.ERROR(f'\n❌ 错误 ({len(errors)}个):'))
            for issue in errors:
                self.display_issue(issue, self.style.ERROR)
        
        if warnings:
            self.stdout.write(self.style.WARNING(f'\n⚠️  警告 ({len(warnings)}个):'))
            for issue in warnings:
                self.display_issue(issue, self.style.WARNING)
        
        if infos:
            self.stdout.write(f'\n💡 建议 ({len(infos)}个):')
            for issue in infos:
                self.display_issue(issue, lambda x: x)
    
    def display_issue(self, issue: Dict[str, Any], style_func):
        """显示单个问题"""
        file_path = issue['file'].replace(settings.BASE_DIR, '').lstrip('/')
        line_info = f":{issue['line']}" if 'line' in issue else ""
        
        self.stdout.write(style_func(f'  {file_path}{line_info}'))
        self.stdout.write(f'    {issue["message"]}')
        
        if 'match' in issue:
            self.stdout.write(f'    代码: {issue["match"][:100]}...')
    
    def fix_issues(self, issues: List[Dict[str, Any]]):
        """修复发现的问题"""
        self.stdout.write(self.style.WARNING('\n开始自动修复...'))
        
        fixed_count = 0
        
        for issue in issues:
            if issue['type'] == 'missing_import':
                if self.fix_missing_import(issue):
                    fixed_count += 1
        
        if fixed_count > 0:
            self.stdout.write(self.style.SUCCESS(f'✅ 已修复 {fixed_count} 个问题'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  没有可以自动修复的问题'))
    
    def fix_missing_import(self, issue: Dict[str, Any]) -> bool:
        """修复缺少导入的问题"""
        try:
            with open(issue['file'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 在其他导入语句后添加StandardResponse导入
            import_lines = []
            other_lines = []
            in_imports = True
            
            for line in content.split('\n'):
                if in_imports and (line.startswith('from ') or line.startswith('import ')):
                    import_lines.append(line)
                elif in_imports and line.strip() == '':
                    import_lines.append(line)
                else:
                    in_imports = False
                    other_lines.append(line)
            
            # 添加StandardResponse导入
            if 'from core.response import StandardResponse' not in import_lines:
                import_lines.append('from core.response import StandardResponse')
            
            # 重新组合内容
            new_content = '\n'.join(import_lines + other_lines)
            
            with open(issue['file'], 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.stdout.write(f'  ✅ 已修复: {issue["file"]}')
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ 修复失败 {issue["file"]}: {str(e)}'))
            return False