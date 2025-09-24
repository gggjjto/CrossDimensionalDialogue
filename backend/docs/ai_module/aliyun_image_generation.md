# 阿里云图像生成使用指南

## 概述

阿里云图像生成功能基于通义万相（WanX）服务，提供高质量的AI图像生成能力。本指南将介绍如何在AI模块中使用阿里云图像生成功能。

## 配置要求

### 环境变量

确保在 `.env` 文件中配置了阿里云API密钥：

```bash
# 阿里云配置
ALIYUN_API_KEY=your_aliyun_api_key
```

### 依赖包

确保安装了 `dashscope` 包：

```bash
pip install dashscope
```

## 使用方法

### 基本使用

```python
from app.services.ai_module import ai_service_manager

# 获取阿里云图像生成服务
service = ai_service_manager.get_service("aliyun_wanx")

# 生成图像
character_data = {
    "character_description": "一只可爱的黄色小鸭子，戴着蓝色帽子",
    "style": "anime",
    "quality": "high",
    "aspect_ratio": "1:1"
}

image_data = await service.generate_character_image(character_data)

# 保存图像
with open("generated_image.png", "wb") as f:
    f.write(image_data)
```

### 支持的参数

#### 图像尺寸 (size)
- `1024*1024` - 正方形 (默认)
- `1024*768` - 横向
- `768*1024` - 纵向
- `1280*720` - 宽屏横向
- `720*1280` - 宽屏纵向
- `1024*576` - 16:9横向
- `576*1024` - 16:9纵向

#### 图像风格 (style)
- `realistic` - 写实风格 (默认)
- `anime` - 动漫风格
- `oil_painting` - 油画风格
- `watercolor` - 水彩风格
- `sketch` - 素描风格

#### 图像质量 (quality)
- `standard` - 标准质量 (默认)
- `hd` - 高清质量

### 高级用法

#### 生成通用图像

```python
# 使用通用图像生成
image_params = {
    "description": "一只美丽的蝴蝶在花丛中飞舞",
    "style": "realistic",
    "quality": "hd",
    "mood": "peaceful",
    "lighting": "soft"
}

image_data = await service.generate_image(image_params)
```

#### 批量生成不同风格的图像

```python
styles = ["anime", "realistic", "oil_painting", "watercolor"]

for style in styles:
    character_data = {
        "character_description": "一只可爱的小猫",
        "style": style,
        "quality": "standard"
    }
    
    image_data = await service.generate_character_image(character_data)
    
    # 保存不同风格的图像
    with open(f"cat_{style}.png", "wb") as f:
        f.write(image_data)
```

#### 生成不同尺寸的图像

```python
sizes = ["1024*1024", "1024*768", "768*1024"]

for size in sizes:
    character_data = {
        "character_description": "一只可爱的小狗",
        "style": "anime",
        "quality": "standard"
    }
    
    image_data = await service.generate_character_image(
        character_data, 
        size=size
    )
    
    # 保存不同尺寸的图像
    filename = f"dog_{size.replace('*', 'x')}.png"
    with open(filename, "wb") as f:
        f.write(image_data)
```

## 提供商能力查询

### 获取支持的模型

```python
service = ai_service_manager.get_service("aliyun_wanx")
provider = service.provider

if hasattr(provider, 'get_supported_models'):
    models = provider.get_supported_models()
    print(f"支持的模型: {models}")
```

### 获取支持的尺寸

```python
if hasattr(provider, 'get_supported_sizes'):
    sizes = provider.get_supported_sizes()
    print(f"支持的尺寸: {sizes}")
```

### 获取支持的风格

```python
if hasattr(provider, 'get_supported_styles'):
    styles = provider.get_supported_styles()
    print(f"支持的风格: {styles}")
```

## 错误处理

### 常见错误

1. **API密钥错误**
```python
try:
    image_data = await service.generate_character_image(character_data)
except Exception as e:
    if "API密钥" in str(e):
        print("请检查ALIYUN_API_KEY环境变量")
```

2. **参数验证错误**
```python
try:
    # 使用无效的尺寸
    image_data = await service.generate_image(
        {"description": "test"}, 
        size="invalid_size"
    )
except Exception as e:
    print(f"参数错误: {e}")
```

3. **网络连接错误**
```python
try:
    image_data = await service.generate_character_image(character_data)
except Exception as e:
    if "网络" in str(e) or "连接" in str(e):
        print("请检查网络连接")
```

### 健康检查

```python
# 检查服务健康状态
health = await service.health_check()
if health:
    print("阿里云图像生成服务正常")
else:
    print("阿里云图像生成服务异常")
```

## 性能优化

### 批量处理

```python
import asyncio

async def batch_generate_images(descriptions):
    """批量生成图像"""
    tasks = []
    
    for desc in descriptions:
        character_data = {
            "character_description": desc,
            "style": "anime",
            "quality": "standard"
        }
        task = service.generate_character_image(character_data)
        tasks.append(task)
    
    # 并发执行
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"第{i+1}个图像生成失败: {result}")
        else:
            print(f"第{i+1}个图像生成成功，大小: {len(result)} 字节")
```

### 缓存机制

```python
import hashlib
import os

class ImageCache:
    def __init__(self, cache_dir="image_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get_cache_key(self, params):
        """生成缓存键"""
        key_str = str(sorted(params.items()))
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def get_or_generate(self, service, params):
        """获取缓存或生成新图像"""
        cache_key = self.get_cache_key(params)
        cache_file = self.cache_dir / f"{cache_key}.png"
        
        if cache_file.exists():
            print(f"使用缓存图像: {cache_file}")
            return cache_file.read_bytes()
        
        # 生成新图像
        image_data = await service.generate_character_image(params)
        
        # 保存到缓存
        cache_file.write_bytes(image_data)
        print(f"图像已缓存: {cache_file}")
        
        return image_data

# 使用缓存
cache = ImageCache()
image_data = await cache.get_or_generate(service, character_data)
```

## 测试

运行专门的阿里云图像生成测试：

```bash
cd backend
python app/scripts/test_aliyun_image_generation.py
```

这将测试：
- 角色图像生成
- 通用图像生成
- 不同风格的图像生成
- 不同尺寸的图像生成
- 服务信息查询
- 健康检查

## 注意事项

1. **API限制**: 阿里云通义万相可能有调用频率限制，请根据实际使用情况调整
2. **费用**: 图像生成服务可能产生费用，请查看阿里云官方定价
3. **图像质量**: 不同风格和尺寸的图像质量可能有所差异
4. **网络延迟**: 图像生成和下载可能需要一定时间，建议添加适当的超时处理

## 故障排除

### 问题1: 图像生成失败
- 检查API密钥是否正确配置
- 确认网络连接正常
- 验证输入参数是否有效

### 问题2: 图像质量不佳
- 尝试调整风格参数
- 使用高清质量设置
- 优化提示词描述

### 问题3: 生成速度慢
- 检查网络连接速度
- 考虑使用缓存机制
- 批量处理时注意并发限制

## 总结

阿里云图像生成功能为AI模块提供了强大的图像生成能力，支持多种风格和尺寸。通过合理使用参数和优化策略，可以获得高质量的AI生成图像。
