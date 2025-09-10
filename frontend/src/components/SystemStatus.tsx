import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  Alert,
  CircularProgress,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  HealthAndSafety as HealthIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Api as ApiIcon,
  Storage as StorageIcon,
  Memory as MemoryIcon,
  Speed as PerformanceIcon,
} from '@mui/icons-material';
import { memoryApi } from '../services/api';
import { useUser } from '../contexts/UserContext';

interface SystemHealth {
  status: string;
  service: string;
  version: string;
}

const SystemStatus: React.FC = () => {
  const { currentUser } = useUser();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [apiStatus, setApiStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  const checkSystemHealth = async () => {
    setLoading(true);
    setError(null);
    setApiStatus('checking');

    try {
      const health = await memoryApi.healthCheck();
      setSystemHealth(health);
      setApiStatus('online');
      setLastCheck(new Date());
    } catch (err: any) {
      setError(err.message || 'API 连接失败');
      setApiStatus('offline');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkSystemHealth();
    
    // 定期检查系统状态
    const interval = setInterval(checkSystemHealth, 30000); // 30秒检查一次
    
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'online':
        return 'success';
      case 'offline':
        return 'error';
      case 'checking':
        return 'info';
      default:
        return 'warning';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'online':
        return <CheckIcon />;
      case 'offline':
        return <ErrorIcon />;
      case 'checking':
        return <CircularProgress size={20} />;
      default:
        return <ErrorIcon />;
    }
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <HealthIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" component="h2">
            系统状态监控
          </Typography>
          <Box sx={{ ml: 'auto' }}>
            <Button
              variant="outlined"
              size="small"
              startIcon={loading ? <CircularProgress size={16} /> : <RefreshIcon />}
              onClick={checkSystemHealth}
              disabled={loading}
            >
              刷新
            </Button>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* 总体状态 */}
        <Paper elevation={1} sx={{ p: 2, mb: 3, bgcolor: 'grey.50' }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip
                  icon={getStatusIcon(apiStatus)}
                  label={`API ${apiStatus === 'online' ? '在线' : apiStatus === 'offline' ? '离线' : '检查中'}`}
                  color={getStatusColor(apiStatus)}
                />
                {systemHealth && (
                  <Chip
                    icon={<CheckIcon />}
                    label={systemHealth.service}
                    color="success"
                    variant="outlined"
                  />
                )}
              </Box>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Box sx={{ textAlign: { xs: 'left', sm: 'right' } }}>
                {lastCheck && (
                  <Typography variant="caption" color="text.secondary">
                    最后检查: {lastCheck.toLocaleTimeString()}
                  </Typography>
                )}
                {systemHealth && (
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                    版本: {systemHealth.version}
                  </Typography>
                )}
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* 详细状态 */}
        <Grid container spacing={2}>
          {/* API 状态 */}
          <Grid item xs={12} sm={6} md={3}>
            <Paper elevation={1} sx={{ p: 2, textAlign: 'center' }}>
              <ApiIcon sx={{ fontSize: 40, color: getStatusColor(apiStatus) + '.main', mb: 1 }} />
              <Typography variant="h6" color={getStatusColor(apiStatus) + '.main'}>
                API 服务
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {apiStatus === 'online' ? '正常运行' : apiStatus === 'offline' ? '连接失败' : '检查中...'}
              </Typography>
            </Paper>
          </Grid>

          {/* 存储状态 */}
          <Grid item xs={12} sm={6} md={3}>
            <Paper elevation={1} sx={{ p: 2, textAlign: 'center' }}>
              <StorageIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
              <Typography variant="h6" color="success.main">
                存储后端
              </Typography>
              <Typography variant="body2" color="text.secondary">
                SQLite 就绪
              </Typography>
            </Paper>
          </Grid>

          {/* 记忆模块 */}
          <Grid item xs={12} sm={6} md={3}>
            <Paper elevation={1} sx={{ p: 2, textAlign: 'center' }}>
              <MemoryIcon sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
              <Typography variant="h6" color="info.main">
                记忆引擎
              </Typography>
              <Typography variant="body2" color="text.secondary">
                智能管理中
              </Typography>
            </Paper>
          </Grid>

          {/* 性能状态 */}
          <Grid item xs={12} sm={6} md={3}>
            <Paper elevation={1} sx={{ p: 2, textAlign: 'center' }}>
              <PerformanceIcon sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
              <Typography variant="h6" color="warning.main">
                系统性能
              </Typography>
              <Typography variant="body2" color="text.secondary">
                监控中
              </Typography>
            </Paper>
          </Grid>
        </Grid>

        {/* 系统信息 */}
        {systemHealth && (
          <Paper elevation={1} sx={{ mt: 3, p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              系统信息
            </Typography>
            <List dense>
              <ListItem>
                <ListItemIcon>
                  <CheckIcon color="success" />
                </ListItemIcon>
                <ListItemText
                  primary="服务状态"
                  secondary={systemHealth.status}
                />
              </ListItem>
              <Divider variant="inset" component="li" />
              <ListItem>
                <ListItemIcon>
                  <ApiIcon color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary="服务名称"
                  secondary={systemHealth.service}
                />
              </ListItem>
              <Divider variant="inset" component="li" />
              <ListItem>
                <ListItemIcon>
                  <CheckIcon color="info" />
                </ListItemIcon>
                <ListItemText
                  primary="版本信息"
                  secondary={systemHealth.version}
                />
              </ListItem>
              {currentUser && (
                <>
                  <Divider variant="inset" component="li" />
                  <ListItem>
                    <ListItemIcon>
                      <CheckIcon color="secondary" />
                    </ListItemIcon>
                    <ListItemText
                      primary="当前用户"
                      secondary={`${currentUser.name} (${currentUser.id})`}
                    />
                  </ListItem>
                </>
              )}
            </List>
          </Paper>
        )}

        {/* 连接说明 */}
        <Paper elevation={0} sx={{ mt: 3, p: 2, bgcolor: 'grey.50' }}>
          <Typography variant="body2" color="text.secondary">
            💡 系统说明：
          </Typography>
          <Typography variant="body2" color="text.secondary">
            • API 服务: Memory-X 后端服务状态
          </Typography>
          <Typography variant="body2" color="text.secondary">
            • 存储后端: SQLite/Spanner/Mem0 存储引擎
          </Typography>
          <Typography variant="body2" color="text.secondary">
            • 记忆引擎: 短期/工作/长期记忆管理
          </Typography>
          <Typography variant="body2" color="text.secondary">
            • 系统会每30秒自动检查一次状态
          </Typography>
        </Paper>
      </CardContent>
    </Card>
  );
};

export default SystemStatus;