#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
百炼DashScope API通用客户端配置
为Memory-X智能医疗记忆管理系统提供统一的AI模型访问能力
适用于各种医疗场景和患者信息的通用处理
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class DashScopeConfig:
    """百炼API配置类"""
    api_key: str
    base_url: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    model: str = "qwen-max"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    max_tokens: int = 2000
    temperature: float = 0.1
    
    # 医疗专用配置
    medical_mode: bool = True
    patient_context: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY is required")
        
        # 设置默认患者上下文（可配置的医疗信息）
        if self.medical_mode and not self.patient_context:
            self.patient_context = {
                "patient_name": "患者",
                "age": None,
                "allergies": [],
                "family_history": [],
                "medical_focus": ["糖尿病风险评估", "药物安全", "症状分析"]
            }


class BaseDashScopeClient(ABC):
    """百炼API客户端抽象基类"""
    
    def __init__(self, config: DashScopeConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_session()
    
    def _setup_session(self):
        """设置HTTP会话"""
        self.session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 设置默认请求头
        self.session.headers.update({
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Memory-X-Medical-AI/1.0"
        })
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """生成AI响应（抽象方法）"""
        pass
    
    def _build_medical_system_prompt(self) -> str:
        """构建医疗系统提示词"""
        if not self.config.medical_mode:
            return "你是一位专业的AI助手。"
        
        patient_info = self.config.patient_context or {}
        
        system_prompt = f"""你是一位专业的医疗AI助手，专门为患者提供个性化的医疗咨询和建议。

当前患者信息：
- 姓名：{patient_info.get('patient_name', '患者')}
- 年龄：{patient_info.get('age', '未知') if patient_info.get('age') else '未知'}岁
- 过敏史：{', '.join(patient_info.get('allergies', [])) if patient_info.get('allergies') else '无'}
- 家族病史：{', '.join(patient_info.get('family_history', [])) if patient_info.get('family_history') else '无'}

重要医疗原则：
1. 始终考虑患者的过敏史，避免推荐含有过敏原的药物
2. 重视家族病史，特别关注遗传病风险
3. 提供专业、准确、安全的医疗建议
4. 如遇紧急情况，建议立即就医
5. 所有建议仅供参考，最终诊断需以医生意见为准

请以专业、温和、负责任的态度回答患者问题。"""
        
        return system_prompt
    
    def _log_request(self, prompt: str, response: str):
        """记录请求日志"""
        self.logger.info(f"API Request - Prompt length: {len(prompt)}")
        self.logger.debug(f"API Response: {response[:200]}...")


class StandardDashScopeClient(BaseDashScopeClient):
    """标准百炼API客户端实现"""
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        生成AI响应
        
        Args:
            prompt: 用户输入提示
            **kwargs: 额外参数，可覆盖默认配置
            
        Returns:
            str: AI生成的响应文本
            
        Raises:
            Exception: API调用失败时抛出异常
        """
        try:
            # 构建请求参数
            payload = self._build_payload(prompt, **kwargs)
            
            # 发送请求
            response = self.session.post(
                self.config.base_url,
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            ai_response = self._extract_response_text(result)
            
            # 记录日志
            self._log_request(prompt, ai_response)
            
            return ai_response
            
        except requests.exceptions.RequestException as e:
            error_msg = f"DashScope API request failed: {e}"
            self.logger.error(error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"DashScope API processing failed: {e}"
            self.logger.error(error_msg)
            raise Exception(error_msg) from e
    
    def _build_payload(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """构建API请求载荷"""
        # 合并配置参数
        params = {
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "top_p": kwargs.get("top_p", 0.9),
            "repetition_penalty": kwargs.get("repetition_penalty", 1.1)
        }
        
        # 构建消息列表
        messages = [
            {
                "role": "system",
                "content": self._build_medical_system_prompt()
            },
            {
                "role": "user", 
                "content": prompt
            }
        ]
        
        # 添加历史对话（如果提供）
        if "history" in kwargs:
            history_messages = []
            for msg in kwargs["history"]:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    history_messages.append(msg)
            messages = [messages[0]] + history_messages + [messages[1]]
        
        payload = {
            "model": kwargs.get("model", self.config.model),
            "input": {
                "messages": messages
            },
            "parameters": params
        }
        
        return payload
    
    def _extract_response_text(self, result: Dict[str, Any]) -> str:
        """从API响应中提取文本内容"""
        try:
            if "output" in result and "text" in result["output"]:
                return result["output"]["text"].strip()
            elif "output" in result and "choices" in result["output"]:
                # 处理choices格式的响应
                choices = result["output"]["choices"]
                if choices and len(choices) > 0:
                    return choices[0].get("message", {}).get("content", "").strip()
            else:
                self.logger.warning(f"Unexpected response format: {result}")
                return "响应格式异常，请稍后重试。"
        except Exception as e:
            self.logger.error(f"Failed to extract response text: {e}")
            return "响应解析失败，请稍后重试。"


class StreamingDashScopeClient(BaseDashScopeClient):
    """流式百炼API客户端（用于长对话）"""
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        生成流式AI响应
        注：当前版本返回完整响应，未来版本将支持真正的流式处理
        """
        # 当前先实现非流式版本，保持接口一致性
        standard_client = StandardDashScopeClient(self.config)
        return standard_client.generate_response(prompt, **kwargs)


class MedicalDashScopeClient(StandardDashScopeClient):
    """医疗专用百炼API客户端"""
    
    def __init__(self, config: DashScopeConfig):
        # 强制启用医疗模式
        config.medical_mode = True
        super().__init__(config)
    
    def diagnose_symptoms(self, symptoms: List[str], patient_context: Dict[str, Any] = None) -> str:
        """
        症状诊断分析
        
        Args:
            symptoms: 症状列表
            patient_context: 患者上下文信息
            
        Returns:
            str: 诊断分析结果
        """
        symptoms_text = "、".join(symptoms)
        
        prompt = f"""
请基于以下症状进行医疗分析：

症状：{symptoms_text}

请考虑：
1. 患者的家族病史（如有）
2. 已知过敏史（如有）
3. 年龄因素（如适用）
4. 症状间的关联性和可能的病因
5. 推荐的检查项目和注意事项

请提供专业的医疗分析和建议。
"""
        
        return self.generate_response(prompt, max_tokens=1500)
    
    def medication_safety_check(self, medication: str) -> str:
        """
        药物安全性检查
        
        Args:
            medication: 药物名称
            
        Returns:
            str: 安全性分析结果
        """
        prompt = f"""
请对药物 "{medication}" 进行安全性分析：

需要检查的安全要点：
1. 是否含有已知过敏原成分
2. 是否适合有家族病史的患者使用
3. 对成年患者的适用性
4. 常见副作用和注意事项
5. 用药禁忌和相互作用

请提供详细的安全性评估。
"""
        
        return self.generate_response(prompt, max_tokens=1000)


class DashScopeClientFactory:
    """百炼API客户端工厂类"""
    
    @staticmethod
    def create_client(
        client_type: str = "standard",
        api_key: str = None,
        medical_mode: bool = True,
        **config_kwargs
    ) -> BaseDashScopeClient:
        """
        创建百炼API客户端
        
        Args:
            client_type: 客户端类型 ("standard", "streaming", "medical")
            api_key: API密钥，如果不提供则从环境变量获取
            medical_mode: 是否启用医疗模式
            **config_kwargs: 额外配置参数
            
        Returns:
            BaseDashScopeClient: 客户端实例
        """
        # 获取API密钥
        if not api_key:
            api_key = os.getenv('DASHSCOPE_API_KEY')
            if not api_key:
                raise ValueError("请设置DASHSCOPE_API_KEY环境变量或提供api_key参数")
        
        # 创建配置
        config = DashScopeConfig(
            api_key=api_key,
            medical_mode=medical_mode,
            **config_kwargs
        )
        
        # 根据类型创建客户端
        if client_type == "standard":
            return StandardDashScopeClient(config)
        elif client_type == "streaming":
            return StreamingDashScopeClient(config)
        elif client_type == "medical":
            return MedicalDashScopeClient(config)
        else:
            raise ValueError(f"Unknown client type: {client_type}")
    
    @staticmethod
    def create_medical_client(api_key: str = None, **config_kwargs) -> MedicalDashScopeClient:
        """创建医疗专用客户端（便捷方法）"""
        return DashScopeClientFactory.create_client(
            client_type="medical",
            api_key=api_key,
            **config_kwargs
        )


# 全局客户端实例管理
_global_client = None


def get_global_client(
    client_type: str = "medical",
    force_recreate: bool = False,
    **config_kwargs
) -> BaseDashScopeClient:
    """
    获取全局客户端实例（单例模式）
    
    Args:
        client_type: 客户端类型
        force_recreate: 是否强制重新创建
        **config_kwargs: 配置参数
        
    Returns:
        BaseDashScopeClient: 全局客户端实例
    """
    global _global_client
    
    if _global_client is None or force_recreate:
        _global_client = DashScopeClientFactory.create_client(
            client_type=client_type,
            **config_kwargs
        )
    
    return _global_client


def reset_global_client():
    """重置全局客户端实例"""
    global _global_client
    _global_client = None


# 便捷函数
def quick_ask(question: str, client_type: str = "medical") -> str:
    """
    快速提问（使用全局客户端）
    
    Args:
        question: 问题内容
        client_type: 客户端类型
        
    Returns:
        str: AI回答
    """
    client = get_global_client(client_type=client_type)
    return client.generate_response(question)


def medical_consultation(symptoms: List[str]) -> str:
    """
    医疗咨询便捷函数
    
    Args:
        symptoms: 症状列表
        
    Returns:
        str: 医疗分析结果
    """
    client = get_global_client(client_type="medical")
    if isinstance(client, MedicalDashScopeClient):
        return client.diagnose_symptoms(symptoms)
    else:
        # 降级处理
        symptoms_text = "、".join(symptoms)
        return client.generate_response(f"请分析以下症状：{symptoms_text}")


def check_medication_safety(medication: str) -> str:
    """
    药物安全检查便捷函数
    
    Args:
        medication: 药物名称
        
    Returns:
        str: 安全性分析
    """
    client = get_global_client(client_type="medical")
    if isinstance(client, MedicalDashScopeClient):
        return client.medication_safety_check(medication)
    else:
        # 降级处理
        return client.generate_response(f"请分析药物 {medication} 的安全性，考虑患者的过敏史和家族病史。")


if __name__ == "__main__":
    # 测试代码
    import sys
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    try:
        # 创建医疗客户端
        client = DashScopeClientFactory.create_medical_client()
        
        # 测试基础对话
        response = client.generate_response("你好，我想咨询一些医疗健康相关的问题。")
        print("AI回答:", response)
        
        # 测试症状诊断
        symptoms = ["乏力", "多饮", "多尿"]
        diagnosis = client.diagnose_symptoms(symptoms)
        print("症状诊断:", diagnosis)
        
        # 测试药物安全检查
        safety_check = client.medication_safety_check("二甲双胍")
        print("药物安全检查:", safety_check)
        
    except Exception as e:
        print(f"测试失败: {e}")
        sys.exit(1)