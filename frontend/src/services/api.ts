import axios from 'axios';
import {
  Memory,
  MemoryStats,
  ChatResponse,
  SearchMemoryResponse,
  MedicalDecisionRequest,
  MedicalDecisionResponse
} from '../types/memory';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const memoryApi = {
  // 健康检查
  healthCheck: async (): Promise<{ status: string; service: string; version: string }> => {
    const response = await api.get('/health');
    return response.data;
  },

  // 聊天接口
  chat: async (userId: string, message: string): Promise<ChatResponse> => {
    const response = await api.post('/api/memory/chat', {
      user_id: userId,
      message,
    });
    return response.data;
  },

  // 添加记忆
  addMemory: async (
    userId: string,
    message: string,
    aiResponse?: string,
    entities?: Record<string, any>,
    intent?: string,
    importance: number = 2
  ): Promise<{ success: boolean; result: any; memory_id: string }> => {
    const response = await api.post('/api/memory', {
      user_id: userId,
      message,
      response: aiResponse,
      entities,
      intent,
      importance,
    });
    return response.data;
  },

  // 获取记忆
  getMemories: async (userId: string, query?: string, limit: number = 10): Promise<SearchMemoryResponse> => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (query) params.append('query', query);
    
    const response = await api.get(`/api/memory/${encodeURIComponent(userId)}?${params}`);
    return response.data;
  },

  // 搜索记忆
  searchMemories: async (userId: string, query: string, limit: number = 5): Promise<SearchMemoryResponse> => {
    return memoryApi.getMemories(userId, query, limit);
  },

  // 获取记忆统计
  getMemoryStats: async (userId: string): Promise<{ success: boolean; user_id: string; stats: MemoryStats }> => {
    const response = await api.get(`/api/memory/${encodeURIComponent(userId)}/stats`);
    return response.data;
  },

  // 清空记忆
  clearMemory: async (userId: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.post(`/api/memory/${encodeURIComponent(userId)}/clear`);
    return response.data;
  },

  // 删除记忆（按模式）
  deleteMemoryByPattern: async (userId: string, pattern: string): Promise<{ success: boolean; deleted: number }> => {
    const response = await api.post('/api/memory/delete', {
      user_id: userId,
      pattern,
    });
    return response.data;
  },

  // 医疗决策
  medicalDecision: async (request: MedicalDecisionRequest): Promise<MedicalDecisionResponse> => {
    const response = await api.post('/api/medical/decide', request);
    return response.data;
  },

  // 高级查询
  advancedQuery: async (
    userId: string,
    queryType: 'basic' | 'temporal' | 'entity',
    params: Record<string, any>
  ): Promise<{ success: boolean; query_type: string; result: any }> => {
    const response = await api.post('/api/memory/query', {
      user_id: userId,
      type: queryType,
      params,
    });
    return response.data;
  },
};

export default memoryApi;