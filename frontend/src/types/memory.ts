// Memory-X 前端类型定义

export interface Memory {
  id?: string;
  user_message: string;
  ai_response: string;
  timestamp: string;
  entities?: Record<string, any>;
  intent?: string;
  importance: number;
}

export interface MemoryStats {
  user_id: string;
  short_term_count: number;
  working_memory_size: number;
  total_long_term: number;
  session_id: string;
}

export interface ChatResponse {
  success: boolean;
  response: string;
  user_id: string;
  memory_operations: MemoryOperation[];
  memory_stats: MemoryStats;
}

export interface MemoryOperation {
  type: 'intent_detection' | 'memory_storage' | 'context_analysis';
  operation: string;
  details: string;
}

export interface SearchMemoryResponse {
  success: boolean;
  user_id: string;
  memories: Memory[];
  count: number;
}

export interface MedicalEntry {
  rxnorm: string;
  dose: string;
  frequency: string;
  route: string;
  start: string;
  end?: string;
  provenance: string;
}

export interface MedicalDecisionRequest {
  current: MedicalEntry;
  new: MedicalEntry;
  approximate_time?: boolean;
  high_risk?: boolean;
}

export interface MedicalDecisionResponse {
  success: boolean;
  action: 'MERGE' | 'UPDATE' | 'APPEND';
  confidence: number;
}

export interface User {
  id: string;
  name: string;
  avatar?: string;
}