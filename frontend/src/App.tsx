import React, { useState } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Container,
  AppBar,
  Toolbar,
  Typography,
  Box,
  Tabs,
  Tab,
  Paper,
  IconButton,
  useMediaQuery,
} from '@mui/material';
import {
  Psychology as BrainIcon,
  Brightness4 as DarkIcon,
  Brightness7 as LightIcon,
  GitHub as GitHubIcon,
} from '@mui/icons-material';

import { UserProvider } from './contexts/UserContext';
import ChatInterface from './components/ChatInterface';
import MemoryBrowser from './components/MemoryBrowser';
import MedicalDecision from './components/MedicalDecision';
import UserSelector from './components/UserSelector';
import SystemStatus from './components/SystemStatus';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index}>
    {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
  </div>
);

function App() {
  const [tabValue, setTabValue] = useState(0);
  const [darkMode, setDarkMode] = useState(false);
  const isMobile = useMediaQuery('(max-width:600px)');

  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: {
        main: '#1976d2',
      },
      secondary: {
        main: '#dc004e',
      },
    },
    typography: {
      h4: {
        fontWeight: 600,
      },
      h6: {
        fontWeight: 600,
      },
    },
    components: {
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 12,
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: 8,
          },
        },
      },
    },
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const toggleDarkMode = () => {
    setDarkMode(prev => !prev);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <UserProvider>
        <Box sx={{ flexGrow: 1, minHeight: '100vh', bgcolor: 'background.default' }}>
          {/* 应用栏 */}
          <AppBar position="static" elevation={0}>
            <Toolbar>
              <BrainIcon sx={{ mr: 2 }} />
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                Memory-X 智能记忆管理系统
              </Typography>
              
              <IconButton
                color="inherit"
                onClick={toggleDarkMode}
                sx={{ mr: 1 }}
              >
                {darkMode ? <LightIcon /> : <DarkIcon />}
              </IconButton>
              
              <IconButton
                color="inherit"
                href="https://github.com/ylouis83/memory-x"
                target="_blank"
                rel="noopener noreferrer"
              >
                <GitHubIcon />
              </IconButton>
            </Toolbar>
          </AppBar>

          <Container maxWidth="lg" sx={{ mt: 2, mb: 4 }}>
            {/* 导航标签 */}
            <Paper elevation={1} sx={{ mb: 3 }}>
              <Tabs
                value={tabValue}
                onChange={handleTabChange}
                variant={isMobile ? 'scrollable' : 'fullWidth'}
                scrollButtons="auto"
                sx={{ borderBottom: 1, borderColor: 'divider' }}
              >
                <Tab label="智能对话" />
                <Tab label="记忆浏览" />
                <Tab label="医疗决策" />
                <Tab label="用户管理" />
                <Tab label="系统状态" />
              </Tabs>
            </Paper>

            {/* 标签页内容 */}
            <TabPanel value={tabValue} index={0}>
              <ChatInterface />
            </TabPanel>

            <TabPanel value={tabValue} index={1}>
              <MemoryBrowser />
            </TabPanel>

            <TabPanel value={tabValue} index={2}>
              <MedicalDecision />
            </TabPanel>

            <TabPanel value={tabValue} index={3}>
              <UserSelector />
            </TabPanel>

            <TabPanel value={tabValue} index={4}>
              <SystemStatus />
            </TabPanel>
          </Container>

          {/* 页脚 */}
          <Box
            component="footer"
            sx={{
              py: 3,
              px: 2,
              mt: 'auto',
              backgroundColor: 'grey.100',
              ...(darkMode && {
                backgroundColor: 'grey.900',
              }),
            }}
          >
            <Container maxWidth="lg">
              <Typography variant="body2" color="text.secondary" align="center">
                Memory-X © 2024 - 智能记忆管理系统 |
                基于 Google Vertex AI Memory Bank 设计理念 |
                支持层次化记忆、向量检索、FHIR 医疗标准
              </Typography>
            </Container>
          </Box>
        </Box>
      </UserProvider>
    </ThemeProvider>
  );
}

export default App;
