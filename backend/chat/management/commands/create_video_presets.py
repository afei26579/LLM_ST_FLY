"""
创建视频风格预设数据的管理命令
"""

from django.core.management.base import BaseCommand
from chat.ai-video.models import VideoStylePreset


class Command(BaseCommand):
    help = '创建视频风格预设数据'

    def handle(self, *args, **options):
        """执行命令"""
        presets = [
            {
                'name': '写实风格',
                'description': '高度写实的视频风格，适合商业展示和纪录片',
                'style_keywords': '超写实, 4K高清, 电影级画质, 专业摄影, 自然光线',
                'recommended_model': 'wanx2.1-t2v-turbo',
                'default_resolution': '1920*1080',
                'default_duration': 5,
                'default_fps': 30
            },
            {
                'name': '动漫风格',
                'description': '二次元动漫风格，色彩鲜艳，适合娱乐内容',
                'style_keywords': '动漫风格, 二次元, 鲜艳色彩, 大眼睛, 日式动画',
                'recommended_model': 'wanx2.1-t2v-turbo',
                'default_resolution': '1280*720',
                'default_duration': 5,
                'default_fps': 25
            },
            {
                'name': '科幻风格',
                'description': '未来科技感十足，适合科幻主题视频',
                'style_keywords': '科幻, 未来科技, 霓虹灯, 赛博朋克, 金属质感, 蓝紫色调',
                'recommended_model': 'wanx2.1-t2v-turbo',
                'default_resolution': '1920*1080',
                'default_duration': 5,
                'default_fps': 30
            },
            {
                'name': '古风水墨',
                'description': '中国传统水墨画风格，优雅古典',
                'style_keywords': '水墨画, 中国风, 古典优雅, 淡雅色彩, 山水意境',
                'recommended_model': 'wanx2.1-t2v-turbo',
                'default_resolution': '1280*720',
                'default_duration': 6,
                'default_fps': 24
            },
            {
                'name': '梦幻仙境',
                'description': '梦幻般的仙境风格，色彩柔和浪漫',
                'style_keywords': '梦幻, 仙境, 柔和光线, 粉色调, 浪漫唯美, 童话风格',
                'recommended_model': 'wanx2.1-t2v-turbo',
                'default_resolution': '1280*720',
                'default_duration': 5,
                'default_fps': 25
            },
            {
                'name': '复古胶片',
                'description': '复古胶片相机风格，带有怀旧色调',
                'style_keywords': '复古胶片, 怀旧色调, 颗粒质感, 暖色调, 70年代风格',
                'recommended_model': 'wanx2.1-t2v-turbo',
                'default_resolution': '1280*720',
                'default_duration': 5,
                'default_fps': 24
            },
            {
                'name': '简约扁平',
                'description': '现代简约的扁平化设计风格',
                'style_keywords': '扁平化设计, 简约风格, 几何图形, 纯色背景, 现代设计',
                'recommended_model': 'wanx2.1-t2v-turbo',
                'default_resolution': '1280*720',
                'default_duration': 4,
                'default_fps': 30
            },
            {
                'name': '油画风格',
                'description': '经典油画艺术风格，具有艺术价值',
                'style_keywords': '油画风格, 艺术绘画, 厚重笔触, 丰富色彩, 古典美术',
                'recommended_model': 'wanx2.1-t2v-turbo',
                'default_resolution': '1280*720',
                'default_duration': 6,
                'default_fps': 24
            }
        ]

        created_count = 0
        for preset_data in presets:
            preset, created = VideoStylePreset.objects.get_or_create(
                name=preset_data['name'],
                defaults=preset_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ 已创建风格预设: {preset.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'→ 风格预设已存在: {preset.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 操作完成！共创建了 {created_count} 个新的视频风格预设')
        )
