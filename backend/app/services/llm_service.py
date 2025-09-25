import logging
from typing import List, Optional, Dict

import dashscope
from dashscope import Generation

from sqlmodel import Session

from app.models.character import Character
from app.models.conversation import Conversation, Message
from app.models.conversation import SenderType
from app.crud.conversation import message as message_crud
from app.core.config import settings
from app.schemas.character import CharacterGenerateRequest, CharacterGenerateResponse
import json
import re
logger = logging.getLogger(__name__)


class LLMRequest:
    """LLM请求模型"""

    def __init__(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 0.9,
        model: Optional[str] = None,
    ):
        self.messages = messages
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.model = model or "qwen-plus"


class LLMResponse:
    """LLM响应模型"""

    def __init__(
        self,
        content: str,
        model: str,
        usage: Optional[Dict[str, int]] = None,
        finish_reason: Optional[str] = None,
    ):
        self.content = content
        self.model = model
        self.usage = usage or {}
        self.finish_reason = finish_reason


class LLMService:
    """LLM服务类 - 使用AI模块"""

    def __init__(self):
        # 初始化 dashscope api_key
        dashscope.api_key = settings.QWEN_API_KEY

    async def generate_character_response(
        self,
        character: Character,
        conversation: Optional[Conversation] = None,
        user_message: str = "",
        session: Optional[Session] = None,
        conversation_history: Optional[List[Message]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """
        生成角色回复 - 调用 qwen-plus 模型
        """
        try:
            # 构建消息
            if conversation_history:
                messages = conversation_history
            elif conversation and session:
                messages = self._build_messages(character, conversation, user_message, session)
            else:
                # 只用用户消息
                messages = [
                    {"role": "system", "content": self._build_system_prompt(character)},
                    {"role": "user", "content": user_message},
                ]

            # 调用 qwen-plus 模型
            response = Generation.call(
                model="qwen-plus",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9,
            )

            content = response.output.text
            usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            }

            return LLMResponse(
                content=content,
                model="qwen-plus",
                usage=usage
            )

        except Exception as e:
            logger.error(f"生成角色回复失败: {str(e)}")
            return LLMResponse(
                content="抱歉，我现在无法回复。请稍后再试。",
                model="fallback",
                usage={},
            )

    def _build_messages(
        self,
        character: Character,
        conversation: Conversation,
        user_message: str,
        session: Session,
    ) -> List[Dict[str, str]]:
        messages = []
        system_prompt = self._build_system_prompt(character)
        messages.append({"role": "system", "content": system_prompt})

        recent_messages = message_crud.get_recent_messages(
            session, conversation_id=conversation.id, limit=30
        )

        for msg in recent_messages:
            if msg.sender_type == SenderType.USER:
                messages.append({"role": "user", "content": msg.content})
            elif msg.sender_type == SenderType.CHARACTER:
                messages.append({"role": "assistant", "content": msg.content})

        messages.append({"role": "user", "content": user_message})

        return messages

    def _build_system_prompt(self, character: Character) -> str:
        prompt_parts = []
        prompt_parts.append(f"你是{character.name}。")
        if character.short_bio:
            prompt_parts.append(f"简介：{character.short_bio}")
        if character.persona_text:
            prompt_parts.append(f"角色设定：{character.persona_text}")
        if character.example_lines:
            prompt_parts.append("示例台词：")
            for line in character.example_lines:
                prompt_parts.append(f"- {line}")
        prompt_parts.extend(
            [
                "",
                "请按照以上设定进行对话，保持角色的一致性。",
                "回复要自然、有趣，符合角色的性格特点。",
                "每次回复控制在200字以内。",
            ]
        )
        return "\n".join(prompt_parts)


    def generate_character_profile(self, request: CharacterGenerateRequest, temperature: float = 0.7, max_tokens: int = 2000) -> CharacterGenerateResponse:
        """
        生成角色简介
        """
        try:
            system_prompt = self._build_character_generation_system_prompt()
            user_prompt = self._build_character_generation_user_prompt(request)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            response = Generation.call(
                model="qwen-plus",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9,
            )

            content = response.output.text
            parsed_result = self._parse_character_generation_response(content, request)

            return parsed_result
        
        except Exception as e:
            logger.error(f"生成角色简介失败: {str(e)}")
            return None

    def _build_character_generation_system_prompt(self) -> str:
        """构建角色生成系统提示词"""
        return f"""你是一个专业的角色设定生成器。请根据用户提供的信息，生成一个完整、详细、有趣的角色设定。
请按照以下JSON格式输出结果：
{
    "name": "角色名称",
    "short_bio": "角色简介（50-100字）",
    "persona_text": "详细人格设定（200-300字）",
    "example_lines": ["示例对话1", "示例对话2", "示例对话3"],
    "suggested_voice": "推荐音色",
    "character_analysis": "角色分析（100-150字）"
}
示例1：
{
    "name": "花木兰",
    "short_bio": "中国古代传奇女英雄，代父从军",
    "persona_text": "我是花木兰，我代父从军，忠诚与勇敢是我的信念。我珍视友情，也有自己的爱情故事。",
    "example_lines": ["巾帼不让须眉", "忠孝两全是我的追求"],
    "suggested_voice": "Ethan",
}
示例2：
{
    "name": "孙悟空",
    "short_bio": "中国古代神话中的传奇人物，齐天大圣",
    "persona_text": "我是孙悟空，我机智勇敢，喜欢恶作剧，但也有一颗正义的心。",
    "example_lines": ["我是齐天大圣孙悟空", "我喜欢吃桃子"],
    "suggested_voice": "Ryan",
}

要求：
1. 角色设定要生动有趣，有独特的个性
2. 示例对话要体现角色的性格特点
3. 推荐音色要符合角色特征
5. 所有文本都要用中文
6. 音色有17种, 请从17种音色中选择一个, 分别是：
"南京-老李"	"li"	"耐心的瑜伽老师"
"四川-晴儿"	"Sunny"	"甜到你心里的川妹子"
"北京-晓东"	"Dylan"	"北京胡同里长大的少年。"
"上海-阿珍"	"Jada"	"沪上阿姐，风风火火"
"墨讲师"	"Elias"	"严谨叙事，适合知识讲解。"
"卡捷琳娜"	"Katerina"	"御姐音色，韵律回味十足。"
"甜茶"	"Ryan"	"节奏拉满，戏感炸裂，真实与张力共舞。"
"詹妮弗"	"Jennifer"	"品牌级、电影质感般美语女声。"
"不吃鱼"	"Nofish"	"不会翘舌音的设计师。"
"晨煦"	"Ethan"	"标准普通话，带部分北方口音。阳光、温暖、活力、朝气。"
"芊悦"	"Cherry"	"阳光积极、亲切自然小姐姐。"
"四川-程川"	"Eric"	"一个跳脱市井的四川成都男子。"
"粤语-阿清"	"Kiki"	"甜美港风闺蜜"
"粤语-阿强"	"Rocky"	"幽默风趣，在线陪聊"
"天津-李彼得"	"Peter"	"相声捧哏风格"
"闽南-阿杰"	"Roy"	"诙谐直爽、市井活泼的台湾哥仔形象。"
"陕西-秦川"	"Marcus"	"面宽话短，心实声沉"
7. 不要输出任何其他内容，只输出JSON格式
"""

    def _build_character_generation_user_prompt(self, request: CharacterGenerateRequest) -> str:
        """构建角色生成用户提示词"""
        prompt_parts = []
        prompt_parts.append(f"请为以下角色生成详细设定：")
        prompt_parts.append(f"角色名称：{request.name}")
        prompt_parts.append(f"角色类型：{request.character_type}")
        
        if request.background:
            prompt_parts.append(f"背景描述：{request.background}")
        prompt_parts.append("\n请生成一个完整、有趣的角色设定。")
        
        return "\n".join(prompt_parts)

        
    def _parse_character_generation_response(self, content: str, request: CharacterGenerateRequest) -> CharacterGenerateResponse:
        """解析LLM响应为结构化数据"""
        # 尝试提取JSON部分
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            data = json.loads(json_str)
        else:
            raise ValueError("无法解析，请联系管理员")

        return CharacterGenerateResponse(**data)

# 全局LLM服务实例
llm_service = LLMService()
