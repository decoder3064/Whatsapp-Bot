import api from './axios';

export const getWorkers = (params) =>
  api.get('/workers', { params });

export const getWorker = (id) =>
  api.get(`/workers/${id}`);

export const createWorker = (data) =>
  api.post('/workers', data);

export const updateWorker = (id, data) =>
  api.put(`/workers/${id}`, data);

export const deleteWorker = (id) =>
  api.delete(`/workers/${id}`);
