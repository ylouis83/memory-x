import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import type { User } from '../types/memory';

interface UserContextType {
  currentUser: User | null;
  setCurrentUser: (user: User | null) => void;
  users: User[];
  addUser: (user: User) => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

const DEFAULT_USERS: User[] = [
  { id: 'demo_user', name: '演示用户', avatar: '👤' },
  { id: 'medical_user', name: '医疗用户', avatar: '🏥' },
  { id: 'test_user', name: '测试用户', avatar: '🧪' },
];

export const UserProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [users, setUsers] = useState<User[]>(DEFAULT_USERS);

  // 从localStorage加载用户信息
  useEffect(() => {
    const savedUser = localStorage.getItem('memory-x-current-user');
    const savedUsers = localStorage.getItem('memory-x-users');
    
    if (savedUser) {
      setCurrentUser(JSON.parse(savedUser));
    } else {
      setCurrentUser(DEFAULT_USERS[0]); // 默认选择第一个用户
    }
    
    if (savedUsers) {
      setUsers(JSON.parse(savedUsers));
    }
  }, []);

  // 保存当前用户到localStorage
  useEffect(() => {
    if (currentUser) {
      localStorage.setItem('memory-x-current-user', JSON.stringify(currentUser));
    }
  }, [currentUser]);

  // 保存用户列表到localStorage
  useEffect(() => {
    localStorage.setItem('memory-x-users', JSON.stringify(users));
  }, [users]);

  const addUser = (user: User) => {
    setUsers(prev => [...prev.filter(u => u.id !== user.id), user]);
  };

  return (
    <UserContext.Provider value={{
      currentUser,
      setCurrentUser,
      users,
      addUser,
    }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};