import axios from "axios";
import type { AuthResponse, BoardDetail, Task, TaskStatus, User } from "./types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000/api",
});

const TOKEN_KEY = "teamboard_token";

export function setToken(token: string | null) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      setToken(null);
    }
    return Promise.reject(error);
  },
);

export const authApi = {
  login: (email: string, password: string) =>
    api.post<AuthResponse>("/auth/login", { email, password }).then((r) => r.data),
  register: (email: string, full_name: string, password: string, role: string) =>
    api.post<AuthResponse>("/auth/register", { email, full_name, password, role }).then((r) => r.data),
  me: () => api.get<User>("/auth/me").then((r) => r.data),
  users: () => api.get<User[]>("/auth/users").then((r) => r.data),
};

export const boardApi = {
  list: () => api.get("/boards").then((r) => r.data),
  detail: (id: number) => api.get<BoardDetail>(`/boards/${id}`).then((r) => r.data),
  create: (title: string, description = "") =>
    api.post("/boards", { title, description }).then((r) => r.data),
  createTask: (boardId: number, payload: Partial<Task>) =>
    api.post<Task>(`/boards/${boardId}/tasks`, payload).then((r) => r.data),
  updateTask: (boardId: number, taskId: number, payload: Partial<Task>) =>
    api.patch<Task>(`/boards/${boardId}/tasks/${taskId}`, payload).then((r) => r.data),
  moveTask: (boardId: number, taskId: number, status: TaskStatus, position: number) =>
    api.patch<Task>(`/boards/${boardId}/tasks/${taskId}/move`, { status, position }).then((r) => r.data),
  deleteTask: (boardId: number, taskId: number) =>
    api.delete(`/boards/${boardId}/tasks/${taskId}`),
};

export default api;
