import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemSecondary,
  Chip,
  Alert,
  CircularProgress,
  Paper,
  Tab,
  Tabs,
  Divider,
  IconButton,
} from '@mui/material';
import {
  Search as SearchIcon,
  Memory as MemoryIcon,
  Refresh as RefreshIcon,
  AccessTime as TimeIcon,
  Star as ImportanceIcon,
  Psychology as BrainIcon,
} from '@mui/icons-material';
import { memoryApi } from '../services/api';
import { useUser } from '../contexts/UserContext';
import { Memory, MemoryStats } from '../types/memory';
import { format } from 'date-fns';
import { zhCN } from 'date-fns/locale';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index}>
    {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
  </div>
);

const MemoryBrowser: React.FC = () => {
  const { currentUser } = useUser();
  const [tabValue, setTabValue] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // 短期记忆
  const [shortTermMemories, setShortTermMemories] = useState<Memory[]>([]);
  
  // 长期记忆搜索结果
  const [searchResults, setSearchResults] = useState<Memory[]>([]);
  
  // 记忆统计
  const [memoryStats, setMemoryStats] = useState<MemoryStats | null>(null);

  // 加载短期记忆
  const loadShortTermMemories = async () => {
    if (!currentUser) return;
    
    setLoading(true);
    try {
      const response = await memoryApi.getMemories(currentUser.id, '', 10);
      setShortTermMemories(response.memories);
    } catch (err: any) {
      setError(err.response?.data?.error || '加载短期记忆失败');
    } finally {
      setLoading(false);
    }
  };

  // 搜索长期记忆
  const searchLongTermMemories = async () => {
    if (!currentUser || !searchQuery.trim()) return;
    
    setLoading(true);
    try {
      const response = await memoryApi.searchMemories(currentUser.id, searchQuery, 10);
      setSearchResults(response.memories);
    } catch (err: any) {
      setError(err.response?.data?.error || '搜索记忆失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载记忆统计
  const loadMemoryStats = async () => {
    if (!currentUser) return;
    
    try {
      const response = await memoryApi.getMemoryStats(currentUser.id);
      setMemoryStats(response.stats);
    } catch (err: any) {
      setError(err.response?.data?.error || '加载统计失败');
    }
  };

  useEffect(() => {
    if (currentUser) {
      loadShortTermMemories();
      loadMemoryStats();
    }
  }, [currentUser]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setError(null);
  };

  const handleSearchKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      searchLongTermMemories();
    }
  };

  const getImportanceColor = (importance: number) => {
    if (importance >= 4) return 'error';
    if (importance >= 3) return 'warning';
    if (importance >= 2) return 'info';
    return 'default';
  };

  const getImportanceLabel = (importance: number) => {
    if (importance >= 4) return '紧急';
    if (importance >= 3) return '重要';
    if (importance >= 2) return '中等';
    return '普通';
  };

  const renderMemoryItem = (memory: Memory, index: number) => (
    <ListItem key={index} divider>
      <ListItemText
        primary={
          <Box>
            <Typography variant="body1" component="div">
              <strong>用户：</strong> {memory.user_message}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              <strong>AI：</strong> {memory.ai_response}
            </Typography>
          </Box>
        }
        secondary={
          <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1, alignItems: 'center' }}>
            <Chip
              size="small"
              icon={<TimeIcon />}
              label={format(new Date(memory.timestamp), 'MM-dd HH:mm', { locale: zhCN })}
              variant="outlined"
            />
            <Chip
              size="small"
              icon={<ImportanceIcon />}
              label={getImportanceLabel(memory.importance)}
              color={getImportanceColor(memory.importance)}
            />
            {memory.intent && (
              <Chip
                size="small"
                label={memory.intent}
                color="secondary"
                variant="outlined"
              />
            )}
            {memory.entities && Object.keys(memory.entities).length > 0 && (
              <Chip
                size="small"
                label={`实体: ${Object.keys(memory.entities).length}`}
                color="info"
                variant="outlined"
              />
            )}
          </Box>
        }
      />
    </ListItem>
  );

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <MemoryIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" component="h2">
            记忆浏览器
          </Typography>
          <Box sx={{ ml: 'auto' }}>
            <IconButton onClick={() => {
              loadShortTermMemories();
              loadMemoryStats();
            }}>
              <RefreshIcon />
            </IconButton>
          </Box>
        </Box>

        {/* 记忆统计 */}
        {memoryStats && (
          <Paper elevation={1} sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
            <Typography variant="subtitle2" gutterBottom>
              记忆统计
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h6" color="primary">
                    {memoryStats.short_term_count}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    短期记忆
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h6" color="secondary">
                    {memoryStats.working_memory_size}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    工作记忆
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h6" color="success.main">
                    {memoryStats.total_long_term}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    长期记忆
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h6" color="warning.main">
                    {memoryStats.session_id.split('_')[1]}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    会话日期
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* 标签页 */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="短期记忆" />
            <Tab label="长期记忆搜索" />
          </Tabs>
        </Box>

        {/* 短期记忆标签页 */}
        <TabPanel value={tabValue} index={0}>
          <Typography variant="subtitle1" gutterBottom>
            最近对话记录 (最新10条)
          </Typography>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : shortTermMemories.length > 0 ? (
            <List>
              {shortTermMemories.map((memory, index) => renderMemoryItem(memory, index))}
            </List>
          ) : (
            <Paper elevation={0} sx={{ p: 3, textAlign: 'center', bgcolor: 'grey.50' }}>
              <BrainIcon sx={{ fontSize: 48, color: 'grey.400', mb: 1 }} />
              <Typography color="text.secondary">
                暂无短期记忆，开始对话创建记忆吧！
              </Typography>
            </Paper>
          )}
        </TabPanel>

        {/* 长期记忆搜索标签页 */}
        <TabPanel value={tabValue} index={1}>
          <Box sx={{ mb: 3 }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="搜索长期记忆...（例如：头痛、药物、过敏）"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleSearchKeyPress}
              InputProps={{
                endAdornment: (
                  <Button
                    variant="contained"
                    startIcon={<SearchIcon />}
                    onClick={searchLongTermMemories}
                    disabled={!searchQuery.trim() || loading}
                  >
                    搜索
                  </Button>
                ),
              }}
            />
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : searchResults.length > 0 ? (
            <>
              <Typography variant="subtitle2" gutterBottom>
                找到 {searchResults.length} 条相关记忆
              </Typography>
              <List>
                {searchResults.map((memory, index) => renderMemoryItem(memory, index))}
              </List>
            </>
          ) : searchQuery.trim() ? (
            <Paper elevation={0} sx={{ p: 3, textAlign: 'center', bgcolor: 'grey.50' }}>
              <SearchIcon sx={{ fontSize: 48, color: 'grey.400', mb: 1 }} />
              <Typography color="text.secondary">
                未找到匹配的记忆，尝试其他关键词
              </Typography>
            </Paper>
          ) : (
            <Paper elevation={0} sx={{ p: 3, textAlign: 'center', bgcolor: 'grey.50' }}>
              <Typography variant="body2" color="text.secondary">
                💡 搜索提示：
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • 搜索症状：头痛、发热、咳嗽
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • 搜索药物：布洛芬、阿司匹林
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • 搜索过敏：青霉素过敏、药物过敏
              </Typography>
            </Paper>
          )}
        </TabPanel>
      </CardContent>
    </Card>
  );
};

export default MemoryBrowser;