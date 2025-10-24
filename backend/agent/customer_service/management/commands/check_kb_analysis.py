"""
检查知识库的文档分析数据
"""
from django.core.management.base import BaseCommand
from agent.customer_service.models_extended import KnowledgeBase


class Command(BaseCommand):
    help = '检查知识库的文档分析数据'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n========== 知识库分析数据检查 ==========\n'))
        
        kbs = KnowledgeBase.objects.all()
        
        if not kbs:
            self.stdout.write(self.style.WARNING('没有找到任何知识库'))
            return
        
        for kb in kbs:
            self.stdout.write(self.style.HTTP_INFO(f'\n知识库 ID: {kb.id}'))
            self.stdout.write(f'名称: {kb.name}')
            self.stdout.write(f'状态: {kb.status}')
            self.stdout.write(f'文档数: {kb.document_count}')
            self.stdout.write(f'切片数: {kb.chunk_count}')
            self.stdout.write('-' * 50)
            
            # 检查分析结果
            self.stdout.write(self.style.WARNING('📊 文档分析结果：'))
            
            if kb.domain:
                self.stdout.write(f'  ✅ 文档领域: {kb.domain}')
            else:
                self.stdout.write(self.style.ERROR('  ❌ 文档领域: 未生成'))
            
            if kb.summary:
                self.stdout.write(f'  ✅ 文档总结: {kb.summary[:100]}...' if len(kb.summary) > 100 else f'  ✅ 文档总结: {kb.summary}')
            else:
                self.stdout.write(self.style.ERROR('  ❌ 文档总结: 未生成'))
            
            if kb.keywords:
                self.stdout.write(f'  ✅ 关键词: {kb.keywords}')
            else:
                self.stdout.write(self.style.ERROR('  ❌ 关键词: 未生成'))
            
            if kb.key_points:
                self.stdout.write(f'  ✅ 核心要点: {len(kb.key_points)} 条')
                for i, point in enumerate(kb.key_points[:3], 1):
                    self.stdout.write(f'     {i}. {point}')
            else:
                self.stdout.write(self.style.ERROR('  ❌ 核心要点: 未生成'))
            
            if kb.suggested_questions:
                self.stdout.write(f'  ✅ 推荐问题: {len(kb.suggested_questions)} 条')
                for i, q in enumerate(kb.suggested_questions, 1):
                    self.stdout.write(f'     {i}. {q}')
            else:
                self.stdout.write(self.style.ERROR('  ❌ 推荐问题: 未生成'))
            
            if kb.intent_prompt:
                self.stdout.write(f'  ✅ 意图识别提示词: {kb.intent_prompt[:150]}...' if len(kb.intent_prompt) > 150 else f'  ✅ 意图识别提示词: {kb.intent_prompt}')
            else:
                self.stdout.write(self.style.ERROR('  ❌ 意图识别提示词: 未生成'))
            
            # 检查关联的助手
            self.stdout.write('\n🤖 关联的助手：')
            assistants = kb.assistants.all()
            if assistants:
                for assistant in assistants:
                    self.stdout.write(f'  - {assistant.name} (ID: {assistant.id})')
            else:
                self.stdout.write(self.style.WARNING('  暂无助手使用此知识库'))
            
            self.stdout.write('\n')
        
        self.stdout.write(self.style.SUCCESS('\n========== 检查完成 ==========\n'))

