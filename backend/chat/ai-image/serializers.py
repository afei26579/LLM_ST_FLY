"""
AI图像生成序列化器
用于验证和处理图像生成请求参数
"""

from rest_framework import serializers


class ImageGenerationRequestSerializer(serializers.Serializer):
    """图像生成请求序列化器"""
    
    # 正向提示词（必填）
    prompt = serializers.CharField(
        max_length=2000,
        required=True,
        help_text="正向提示词，描述希望在画面中看到的内容、主体、场景、风格、光照和构图"
    )
    
    # 反向提示词（可选）
    negative_prompt = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True,
        help_text="反向提示词，描述不希望在画面中出现的内容"
    )
    
    # 图像分辨率
    size = serializers.ChoiceField(
        choices=[
            ('1328*1328', '1:1 (1328x1328)'),
            ('1664*928', '16:9 (1664x928)'),
            ('928*1664', '9:16 (928x1664)'),
            ('1472*1140', '4:3 (1472x1140)'),
            ('1140*1472', '3:4 (1140x1472)'),
        ],
        default='1328*1328',
        help_text="输出图像分辨率"
    )
    
    # 生成图片数量（固定为1）
    n = serializers.IntegerField(
        default=1,
        required=False,
        help_text="生成图片数量，固定为1张"
    )
    
    def validate_n(self, value):
        """验证生成数量，固定为1"""
        return 1
    
    # 是否开启prompt智能改写
    prompt_extend = serializers.BooleanField(
        default=True,
        help_text="是否开启prompt智能改写，可自动扩展和优化较短的Prompt"
    )
    
    # 是否添加水印
    watermark = serializers.BooleanField(
        default=True,
        help_text="是否添加水印"
    )
    
    # 预设风格（可选）
    style = serializers.ChoiceField(
        choices=[
            ('', '默认'),
            ('3d_cartoon', '3D卡通'),
            ('wasteland', '废土风'),
            ('pointillism', '点彩画'),
            ('surreal', '超现实'),
            ('watercolor', '水彩'),
            ('clay', '粘土'),
            ('realistic', '写实'),
            ('ceramic', '陶瓷'),
            ('3d', '3D'),
            ('ink_wash', '水墨'),
            ('origami', '折纸'),
            ('meticulous', '工笔'),
            ('chinese_style', '国风水墨'),
        ],
        required=False,
        allow_blank=True,
        help_text="预设风格"
    )
    
    # 景别
    shot_type = serializers.ChoiceField(
        choices=[
            ('', '默认'),
            ('long_shot', '远景'),
            ('full_shot', '全景'),
            ('medium_shot', '中景'),
            ('close_up', '近景'),
            ('extreme_close_up', '特写'),
        ],
        required=False,
        allow_blank=True,
        help_text="拍摄景别"
    )
    
    # 视角
    angle = serializers.ChoiceField(
        choices=[
            ('', '默认'),
            ('eye_level', '平视'),
            ('high_angle', '俯视'),
            ('low_angle', '仰视'),
            ('aerial', '航拍'),
        ],
        required=False,
        allow_blank=True,
        help_text="拍摄视角"
    )
    
    # 拍摄技法
    shooting_technique = serializers.ChoiceField(
        choices=[
            ('', '默认'),
            ('macro', '微距'),
            ('ultra_wide', '超广角'),
            ('telephoto', '长焦'),
            ('fisheye', '鱼眼'),
        ],
        required=False,
        allow_blank=True,
        help_text="拍摄技法"
    )
    
    # 光线效果
    lighting = serializers.ChoiceField(
        choices=[
            ('', '默认'),
            ('natural', '自然光'),
            ('backlight', '逆光'),
            ('neon', '霓虹灯'),
            ('ambient', '氛围光'),
        ],
        required=False,
        allow_blank=True,
        help_text="光线效果"
    )

    def validate_prompt(self, value):
        """验证正向提示词"""
        if not value or not value.strip():
            raise serializers.ValidationError("正向提示词不能为空")
        
        # 检查是否包含敏感词汇（这里可以根据需要扩展）
        sensitive_words = ['暴力', '血腥', '色情', '政治']
        for word in sensitive_words:
            if word in value:
                raise serializers.ValidationError(f"提示词中不能包含敏感内容: {word}")
        
        return value.strip()

    def validate_negative_prompt(self, value):
        """验证反向提示词"""
        if value:
            return value.strip()
        return value

    def to_internal_value(self, data):
        """数据预处理"""
        # 调用父类验证
        validated_data = super().to_internal_value(data)
        
        # 构建完整的提示词
        prompt_parts = [validated_data['prompt']]
        
        # 添加风格描述
        if validated_data.get('style'):
            style_map = {
                '3d_cartoon': '3D卡通风格',
                'wasteland': '废土风格',
                'pointillism': '点彩画风格',
                'surreal': '超现实主义风格',
                'watercolor': '水彩画风格',
                'clay': '粘土风格',
                'realistic': '写实风格',
                'ceramic': '陶瓷风格',
                '3d': '3D风格',
                'ink_wash': '水墨画风格',
                'origami': '折纸风格',
                'meticulous': '工笔画风格',
                'chinese_style': '国风水墨风格',
            }
            prompt_parts.append(style_map.get(validated_data['style'], ''))
        
        # 添加景别描述
        if validated_data.get('shot_type'):
            shot_map = {
                'long_shot': '远景拍摄',
                'full_shot': '全景拍摄',
                'medium_shot': '中景拍摄',
                'close_up': '近景拍摄',
                'extreme_close_up': '特写拍摄',
            }
            prompt_parts.append(shot_map.get(validated_data['shot_type'], ''))
        
        # 添加视角描述
        if validated_data.get('angle'):
            angle_map = {
                'eye_level': '平视角度',
                'high_angle': '俯视角度',
                'low_angle': '仰视角度',
                'aerial': '航拍视角',
            }
            prompt_parts.append(angle_map.get(validated_data['angle'], ''))
        
        # 添加拍摄技法描述
        if validated_data.get('shooting_technique'):
            technique_map = {
                'macro': '微距摄影',
                'ultra_wide': '超广角镜头',
                'telephoto': '长焦镜头',
                'fisheye': '鱼眼镜头效果',
            }
            prompt_parts.append(technique_map.get(validated_data['shooting_technique'], ''))
        
        # 添加光线效果描述
        if validated_data.get('lighting'):
            lighting_map = {
                'natural': '自然光照',
                'backlight': '逆光效果',
                'neon': '霓虹灯光效果',
                'ambient': '氛围光照',
            }
            prompt_parts.append(lighting_map.get(validated_data['lighting'], ''))
        
        # 组合完整提示词
        validated_data['enhanced_prompt'] = '，'.join(filter(None, prompt_parts))
        
        return validated_data


class ImageGenerationResponseSerializer(serializers.Serializer):
    """图像生成响应序列化器"""
    
    task_id = serializers.CharField(help_text="任务ID")
    status = serializers.CharField(help_text="任务状态")
    images = serializers.ListField(
        child=serializers.DictField(),
        help_text="生成的图像列表"
    )
    usage = serializers.DictField(help_text="使用统计")
    request_id = serializers.CharField(help_text="请求ID")
    enhanced_prompt = serializers.CharField(help_text="增强后的提示词")


class ImageTaskStatusSerializer(serializers.Serializer):
    """图像任务状态查询序列化器"""
    
    task_id = serializers.CharField(
        required=True,
        help_text="任务ID"
    )


class ImageHistorySerializer(serializers.Serializer):
    """图像历史记录序列化器"""
    
    id = serializers.IntegerField(help_text="记录ID")
    prompt = serializers.CharField(help_text="原始提示词")
    enhanced_prompt = serializers.CharField(help_text="增强后的提示词")
    negative_prompt = serializers.CharField(help_text="反向提示词", allow_blank=True)
    size = serializers.CharField(help_text="图像尺寸")
    style = serializers.CharField(help_text="风格", allow_blank=True)
    images = serializers.ListField(
        child=serializers.DictField(),
        help_text="生成的图像列表"
    )
    created_at = serializers.DateTimeField(help_text="创建时间")
    status = serializers.CharField(help_text="生成状态")
