import api from './axios';

export const getDashboard = () =>
  api.get('/metrics/dashboard');

export const getWorkerMetrics = (params) =>
  api.get('/metrics/workers', { params });

export const getSingleWorkerMetrics = (id) =>
  api.get(`/metrics/workers/${id}`);

export const getReminderAnalytics = (params) =>
  api.get('/metrics/reminders', { params });
