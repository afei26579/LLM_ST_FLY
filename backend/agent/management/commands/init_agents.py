"""
初始化智能体数据的管理命令
"""

from django.core.management.base import BaseCommand
from agent.services import ai_agent_service


class Command(BaseCommand):
    help = '初始化智能体数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化智能体数据...')
        
        try:
            ai_agent_service.initialize_agents()
            self.stdout.write(
                self.style.SUCCESS('✅ 智能体数据初始化成功！')
            )
            
            # 显示已创建的智能体
            from agent.models import Agent
            agents = Agent.objects.all()
            self.stdout.write('\n已创建的智能体：')
            for agent in agents:
                self.stdout.write(f'  • {agent.name} ({agent.type})')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 智能体数据初始化失败: {str(e)}')
            )
            return
            
        self.stdout.write('\n' + '='*50)
        self.stdout.write('🎉 智能体功能已准备就绪！')
        self.stdout.write('现在您可以通过前端界面访问智能体功能了。')
        self.stdout.write('='*50)
