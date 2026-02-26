import api from './axios';

export const sendMessage = (message) =>
  api.post('/chat', { message });
