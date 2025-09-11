import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Chip,
  Alert,
  CircularProgress,
  Paper,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import { Send as SendIcon, Psychology as BrainIcon } from '@mui/icons-material';
import { memoryApi } from '../services/api';
import { useUser } from '../contexts/UserContext';
import type { ChatResponse, MemoryOperation } from '../types/memory';

const ChatInterface: React.FC = () => {
  const { currentUser } = useUser();
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatResponse[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleSendMessage = async () => {
    if (!message.trim() || !currentUser || loading) return;

    setLoading(true);
    setError(null);

    try {
      const response = await memoryApi.chat(currentUser.id, message);
      setChatHistory(prev => [...prev, response]);
      setMessage('');
    } catch (err: any) {
      setError(err.response?.data?.error || '发送消息失败');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // const getIntentColor = (intent: string) => {
  //   const colors: Record<string, 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'> = {
  //     'EMERGENCY': 'error',
  //     'REQUEST_MEDICINE': 'warning',
  //     'PRESCRIPTION_INQUIRY': 'info',
  //     'INTRODUCE': 'success',
  //     'NORMAL_CONSULTATION': 'primary',
  //   };
  //   return colors[intent] || 'default';
  // };

  const renderMemoryOperation = (operation: MemoryOperation) => {
    const icons: Record<string, string> = {
      'intent_detection': '🎯',
      'memory_storage': '💾',
      'context_analysis': '🔍',
    };

    return (
      <Box key={operation.type} sx={{ mb: 1 }}>
        <Typography variant="caption" color="text.secondary">
          {icons[operation.type]} {operation.details}
        </Typography>
      </Box>
    );
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <BrainIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" component="h2">
            智能对话记忆
          </Typography>
        </Box>

        {/* 输入区域 */}
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            placeholder="输入您的消息...（例如：我叫张三，今年30岁，最近头痛）"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
          />
          <Box sx={{ mt: 1, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              endIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
              onClick={handleSendMessage}
              disabled={!message.trim() || !currentUser || loading}
            >
              {loading ? '发送中...' : '发送'}
            </Button>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* 对话历史 */}
        {chatHistory.length > 0 && (
          <Paper elevation={1} sx={{ maxHeight: 600, overflow: 'auto', p: 2 }}>
            <Typography variant="h6" gutterBottom>
              对话历史
            </Typography>
            <List>
              {chatHistory.map((chat, index) => (
                <React.Fragment key={index}>
                  <ListItem alignItems="flex-start">
                    <ListItemText
                      primary={
                        <Box>
                          <Typography component="span" variant="body2" color="text.primary">
                            <strong>用户：</strong>
                          </Typography>
                          <Typography component="span" variant="body2" sx={{ ml: 1 }}>
                            {/* 从memory_operations中提取用户消息，这里简化处理 */}
                            {message}
                          </Typography>
                        </Box>
                      }
                      secondary={
                        <Box sx={{ mt: 1 }}>
                          <Typography component="span" variant="body2" color="text.primary">
                            <strong>AI：</strong>
                          </Typography>
                          <Typography component="span" variant="body2" sx={{ ml: 1 }}>
                            {chat.response}
                          </Typography>
                          
                          {/* 记忆操作信息 */}
                          <Box sx={{ mt: 2 }}>
                            <Typography variant="subtitle2" color="text.secondary">
                              记忆处理过程：
                            </Typography>
                            {chat.memory_operations.map((op) => renderMemoryOperation(op))}
                          </Box>

                          {/* 记忆统计 */}
                          {chat.memory_stats && (
                            <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                              <Chip 
                                size="small" 
                                label={`短期记忆: ${chat.memory_stats.short_term_count}`}
                                color="info"
                              />
                              <Chip 
                                size="small" 
                                label={`工作记忆: ${chat.memory_stats.working_memory_size}`}
                                color="secondary"
                              />
                              <Chip 
                                size="small" 
                                label={`长期记忆: ${chat.memory_stats.total_long_term}`}
                                color="success"
                              />
                            </Box>
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < chatHistory.length - 1 && <Divider variant="inset" component="li" />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        )}

        {/* 使用提示 */}
        {chatHistory.length === 0 && (
          <Paper elevation={0} sx={{ bgcolor: 'grey.50', p: 2, mt: 2 }}>
            <Typography variant="body2" color="text.secondary">
              💡 使用提示：
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • 输入个人信息：我叫张三，今年30岁
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • 描述症状：最近头痛，晚上更明显
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • 询问药物：布洛芬怎么吃？有什么副作用？
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • 过敏信息：我对青霉素过敏
            </Typography>
          </Paper>
        )}
      </CardContent>
    </Card>
  );
};

export default ChatInterface;