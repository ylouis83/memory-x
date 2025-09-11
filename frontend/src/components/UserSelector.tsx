import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Avatar,
  Chip,
  Alert,
} from '@mui/material';
import {
  Person as PersonIcon,
  Add as AddIcon,
  AccountCircle as AccountIcon,
} from '@mui/icons-material';
import { useUser } from '../contexts/UserContext';


const UserSelector: React.FC = () => {
  const { currentUser, setCurrentUser, users, addUser } = useUser();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newUser, setNewUser] = useState({ id: '', name: '', avatar: '👤' });
  const [error, setError] = useState<string | null>(null);

  const handleUserChange = (userId: string) => {
    const user = users.find(u => u.id === userId);
    if (user) {
      setCurrentUser(user);
    }
  };

  const handleAddUser = () => {
    if (!newUser.id.trim() || !newUser.name.trim()) {
      setError('请填写用户ID和姓名');
      return;
    }

    if (users.some(u => u.id === newUser.id)) {
      setError('用户ID已存在');
      return;
    }

    addUser({
      id: newUser.id.trim(),
      name: newUser.name.trim(),
      avatar: newUser.avatar || '👤',
    });

    setNewUser({ id: '', name: '', avatar: '👤' });
    setDialogOpen(false);
    setError(null);
  };

  const getStatusColor = (userId: string) => {
    if (!currentUser) return 'default';
    return userId === currentUser.id ? 'primary' : 'default';
  };

  return (
    <>
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <PersonIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6" component="h2">
              用户管理
            </Typography>
          </Box>

          {/* 当前用户显示 */}
          {currentUser && (
            <Box sx={{ mb: 3, p: 2, bgcolor: 'primary.50', borderRadius: 1, border: '1px solid', borderColor: 'primary.200' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  {currentUser.avatar}
                </Avatar>
                <Box>
                  <Typography variant="subtitle1" fontWeight="bold">
                    {currentUser.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    ID: {currentUser.id}
                  </Typography>
                </Box>
                <Chip
                  label="当前用户"
                  color="primary"
                  size="small"
                  sx={{ ml: 'auto' }}
                />
              </Box>
            </Box>
          )}

          {/* 用户选择 */}
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>选择用户</InputLabel>
            <Select
              value={currentUser?.id || ''}
              label="选择用户"
              onChange={(e) => handleUserChange(e.target.value)}
            >
              {users.map((user) => (
                <MenuItem key={user.id} value={user.id}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <span>{user.avatar}</span>
                    <span>{user.name}</span>
                    <Chip
                      size="small"
                      label={user.id}
                      variant="outlined"
                      color={getStatusColor(user.id)}
                    />
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* 添加用户按钮 */}
          <Button
            fullWidth
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={() => setDialogOpen(true)}
          >
            添加新用户
          </Button>

          {/* 用户列表 */}
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              所有用户 ({users.length})
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {users.map((user) => (
                <Chip
                  key={user.id}
                  avatar={<Avatar sx={{ bgcolor: 'transparent' }}>{user.avatar}</Avatar>}
                  label={user.name}
                  variant={user.id === currentUser?.id ? 'filled' : 'outlined'}
                  color={getStatusColor(user.id)}
                  onClick={() => handleUserChange(user.id)}
                  clickable
                />
              ))}
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* 添加用户对话框 */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <AccountIcon sx={{ mr: 1 }} />
            添加新用户
          </Box>
        </DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          <TextField
            fullWidth
            label="用户ID"
            value={newUser.id}
            onChange={(e) => setNewUser(prev => ({ ...prev, id: e.target.value }))}
            placeholder="例如: doctor_wang"
            sx={{ mb: 2 }}
            helperText="用户ID必须唯一，建议使用英文字母和下划线"
          />
          
          <TextField
            fullWidth
            label="用户姓名"
            value={newUser.name}
            onChange={(e) => setNewUser(prev => ({ ...prev, name: e.target.value }))}
            placeholder="例如: 王医生"
            sx={{ mb: 2 }}
          />
          
          <TextField
            fullWidth
            label="头像表情"
            value={newUser.avatar}
            onChange={(e) => setNewUser(prev => ({ ...prev, avatar: e.target.value }))}
            placeholder="例如: 👨‍⚕️"
            helperText="可以使用任何emoji表情"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setDialogOpen(false);
            setError(null);
            setNewUser({ id: '', name: '', avatar: '👤' });
          }}>
            取消
          </Button>
          <Button variant="contained" onClick={handleAddUser}>
            添加
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default UserSelector;