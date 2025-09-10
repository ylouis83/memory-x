import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  FormControlLabel,
  Checkbox,
  Alert,
  CircularProgress,
  Paper,
  Chip,
  Divider,
} from '@mui/material';
import {
  LocalHospital as MedicalIcon,
  Psychology as DecisionIcon,
  Warning as WarningIcon,
  CheckCircle as SuccessIcon,
} from '@mui/icons-material';
import { memoryApi } from '../services/api';
import { MedicalEntry, MedicalDecisionRequest, MedicalDecisionResponse } from '../types/memory';

const MedicalDecision: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<MedicalDecisionResponse | null>(null);

  // 当前记录
  const [currentEntry, setCurrentEntry] = useState<MedicalEntry>({
    rxnorm: '11111',
    dose: '5 mg',
    frequency: 'qd',
    route: 'oral',
    start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: '',
    provenance: 'doctor',
  });

  // 新记录
  const [newEntry, setNewEntry] = useState<MedicalEntry>({
    rxnorm: '11111',
    dose: '5 mg',
    frequency: 'qd',
    route: 'oral',
    start: new Date().toISOString().split('T')[0],
    end: '',
    provenance: 'chat',
  });

  // 选项
  const [approximateTime, setApproximateTime] = useState(false);
  const [highRisk, setHighRisk] = useState(false);

  const handleCurrentEntryChange = (field: keyof MedicalEntry, value: string) => {
    setCurrentEntry(prev => ({ ...prev, [field]: value }));
  };

  const handleNewEntryChange = (field: keyof MedicalEntry, value: string) => {
    setNewEntry(prev => ({ ...prev, [field]: value }));
  };

  const handleDecision = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const request: MedicalDecisionRequest = {
        current: {
          ...currentEntry,
          start: currentEntry.start + 'T00:00:00Z',
          end: currentEntry.end ? currentEntry.end + 'T00:00:00Z' : undefined,
        },
        new: {
          ...newEntry,
          start: newEntry.start + 'T00:00:00Z',
          end: newEntry.end ? newEntry.end + 'T00:00:00Z' : undefined,
        },
        approximate_time: approximateTime,
        high_risk: highRisk,
      };

      const response = await memoryApi.medicalDecision(request);
      setResult(response);
    } catch (err: any) {
      setError(err.response?.data?.error || '医疗决策分析失败');
    } finally {
      setLoading(false);
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case 'MERGE': return 'success';
      case 'UPDATE': return 'warning';
      case 'APPEND': return 'info';
      default: return 'default';
    }
  };

  const getActionDescription = (action: string) => {
    switch (action) {
      case 'MERGE': return '合并记录 - 同一疗程，合并时间区间';
      case 'UPDATE': return '更新记录 - 同一疗程，更新详细信息';
      case 'APPEND': return '新增记录 - 新的独立疗程';
      default: return '未知操作';
    }
  };

  const getConfidenceLevel = (confidence: number) => {
    if (confidence >= 0.8) return { level: '高', color: 'success' as const };
    if (confidence >= 0.6) return { level: '中', color: 'warning' as const };
    return { level: '低', color: 'error' as const };
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <MedicalIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" component="h2">
            医疗记忆决策分析
          </Typography>
        </Box>

        <Typography variant="body2" color="text.secondary" gutterBottom>
          基于 FHIR 风格的用药记忆管理，分析两条用药记录应该进行 MERGE/UPDATE/APPEND 操作
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* 当前记录 */}
          <Grid item xs={12} md={6}>
            <Paper elevation={1} sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom color="primary">
                当前记录
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="RxNorm 代码"
                    value={currentEntry.rxnorm}
                    onChange={(e) => handleCurrentEntryChange('rxnorm', e.target.value)}
                    placeholder="例如: 11111"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="剂量"
                    value={currentEntry.dose}
                    onChange={(e) => handleCurrentEntryChange('dose', e.target.value)}
                    placeholder="例如: 5 mg"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="频率"
                    value={currentEntry.frequency}
                    onChange={(e) => handleCurrentEntryChange('frequency', e.target.value)}
                    placeholder="例如: qd, bid, tid"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="给药途径"
                    value={currentEntry.route}
                    onChange={(e) => handleCurrentEntryChange('route', e.target.value)}
                    placeholder="例如: oral, iv, im"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="来源"
                    value={currentEntry.provenance}
                    onChange={(e) => handleCurrentEntryChange('provenance', e.target.value)}
                    placeholder="例如: doctor, ehr, chat"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="date"
                    label="开始日期"
                    value={currentEntry.start}
                    onChange={(e) => handleCurrentEntryChange('start', e.target.value)}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="date"
                    label="结束日期（可选）"
                    value={currentEntry.end}
                    onChange={(e) => handleCurrentEntryChange('end', e.target.value)}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* 新记录 */}
          <Grid item xs={12} md={6}>
            <Paper elevation={1} sx={{ p: 2, bgcolor: 'grey.50' }}>
              <Typography variant="h6" gutterBottom color="secondary">
                新记录
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="RxNorm 代码"
                    value={newEntry.rxnorm}
                    onChange={(e) => handleNewEntryChange('rxnorm', e.target.value)}
                    placeholder="例如: 11111"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="剂量"
                    value={newEntry.dose}
                    onChange={(e) => handleNewEntryChange('dose', e.target.value)}
                    placeholder="例如: 10 mg"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="频率"
                    value={newEntry.frequency}
                    onChange={(e) => handleNewEntryChange('frequency', e.target.value)}
                    placeholder="例如: bid"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="给药途径"
                    value={newEntry.route}
                    onChange={(e) => handleNewEntryChange('route', e.target.value)}
                    placeholder="例如: oral"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="来源"
                    value={newEntry.provenance}
                    onChange={(e) => handleNewEntryChange('provenance', e.target.value)}
                    placeholder="例如: chat"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="date"
                    label="开始日期"
                    value={newEntry.start}
                    onChange={(e) => handleNewEntryChange('start', e.target.value)}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="date"
                    label="结束日期（可选）"
                    value={newEntry.end}
                    onChange={(e) => handleNewEntryChange('end', e.target.value)}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
              </Grid>
            </Paper>
          </Grid>
        </Grid>

        {/* 分析选项 */}
        <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="subtitle1" gutterBottom>
            分析选项
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={approximateTime}
                    onChange={(e) => setApproximateTime(e.target.checked)}
                  />
                }
                label="时间近似（允许时间差异）"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={highRisk}
                    onChange={(e) => setHighRisk(e.target.checked)}
                  />
                }
                label="高风险药物（提高合并阈值）"
              />
            </Grid>
          </Grid>
        </Box>

        {/* 分析按钮 */}
        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Button
            variant="contained"
            size="large"
            startIcon={loading ? <CircularProgress size={20} /> : <DecisionIcon />}
            onClick={handleDecision}
            disabled={loading}
          >
            {loading ? '分析中...' : '开始决策分析'}
          </Button>
        </Box>

        {/* 分析结果 */}
        {result && (
          <Paper elevation={2} sx={{ mt: 3, p: 3 }}>
            <Typography variant="h6" gutterBottom>
              <SuccessIcon sx={{ mr: 1, color: 'success.main', verticalAlign: 'middle' }} />
              决策分析结果
            </Typography>
            
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={3} alignItems="center">
                <Grid item xs={12} sm={6}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Chip
                      label={result.action}
                      color={getActionColor(result.action)}
                      size="large"
                      sx={{ fontSize: '1.1rem', fontWeight: 'bold', mb: 1 }}
                    />
                    <Typography variant="body2" color="text.secondary">
                      {getActionDescription(result.action)}
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color={getConfidenceLevel(result.confidence).color + '.main'}>
                      {(result.confidence * 100).toFixed(1)}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      置信度: {getConfidenceLevel(result.confidence).level}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>

              <Divider sx={{ my: 2 }} />

              <Box sx={{ bgcolor: 'grey.50', p: 2, borderRadius: 1 }}>
                <Typography variant="subtitle2" gutterBottom>
                  决策说明：
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {result.action === 'MERGE' && '系统检测到这两条记录属于同一疗程，建议合并时间区间以避免重复记录。'}
                  {result.action === 'UPDATE' && '系统检测到新记录是对现有疗程的补充或修正，建议更新现有记录的详细信息。'}
                  {result.action === 'APPEND' && '系统检测到这是一个新的独立疗程，建议作为新记录添加到记忆中。'}
                </Typography>
                
                {result.confidence < 0.6 && (
                  <Alert severity="warning" sx={{ mt: 2 }}>
                    <WarningIcon sx={{ mr: 1 }} />
                    置信度较低，建议人工审核此决策结果
                  </Alert>
                )}
              </Box>
            </Box>
          </Paper>
        )}

        {/* 使用说明 */}
        {!result && (
          <Paper elevation={0} sx={{ mt: 3, p: 2, bgcolor: 'grey.50' }}>
            <Typography variant="body2" color="text.secondary">
              💡 使用说明：
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • MERGE: 同一药物同一疗程的时间区间合并
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • UPDATE: 同一疗程内的剂量、频率等信息更新
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • APPEND: 新的独立用药疗程记录
            </Typography>
          </Paper>
        )}
      </CardContent>
    </Card>
  );
};

export default MedicalDecision;