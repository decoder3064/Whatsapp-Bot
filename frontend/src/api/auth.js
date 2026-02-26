import api from './axios';

export const login = (username, password) =>
  api.post('/auth/login', { username, password });

export const register = (data) =>
  api.post('/auth/register', data);

export const getMe = () =>
  api.get('/auth/me');

export const getUsers = () =>
  api.get('/auth/users');

export const updateUser = (id, data) =>
  api.put(`/auth/users/${id}`, data);
