import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor to inject JWT Access Token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("studymate_access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor to automatically refresh expired tokens
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (
      error.response &&
      error.response.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url.includes("/auth/login") &&
      !originalRequest.url.includes("/auth/refresh")
    ) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem("studymate_refresh_token");
      if (refreshToken) {
        try {
          const res = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
            refresh: refreshToken,
          });
          const newAccess = res.data.access;
          localStorage.setItem("studymate_access_token", newAccess);
          originalRequest.headers.Authorization = `Bearer ${newAccess}`;
          return apiClient(originalRequest);
        } catch (refreshErr) {
          localStorage.removeItem("studymate_access_token");
          localStorage.removeItem("studymate_refresh_token");
          localStorage.removeItem("studymate_user");
          window.dispatchEvent(new Event("auth_logout"));
        }
      }
    }
    return Promise.reject(error);
  }
);

export const api = {
  // Authentication
  auth: {
    register: (username, email, password) =>
      apiClient.post("/auth/register/", { username, email, password }),
    login: (identifier, password) =>
      apiClient.post("/auth/login/", { username: identifier, password }),
    refresh: (refreshToken) =>
      apiClient.post("/auth/refresh/", { refresh: refreshToken }),
    me: () => apiClient.get("/auth/me/"),
  },

  // Document Management
  documents: {
    list: () => apiClient.get("/documents/"),
    get: (id) => apiClient.get(`/documents/${id}/`),
    delete: (id) => apiClient.delete(`/documents/${id}/`),
    upload: (file, onUploadProgress) => {
      const formData = new FormData();
      formData.append("file", file);
      return apiClient.post("/documents/upload/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress,
      });
    },
  },

  // AI Chat & RAG Assistant
  chat: {
    send: (message, conversationId = null) =>
      apiClient.post("/chat/", {
        message,
        conversation_id: conversationId,
      }),
    getHistory: (conversationId) => apiClient.get(`/chat/${conversationId}/`),
  },

  // Quiz Engine
  quiz: {
    generate: (topic, difficulty = "medium", numberOfQuestions = 5) =>
      apiClient.post("/quiz/generate/", {
        topic,
        difficulty,
        number_of_questions: numberOfQuestions,
      }),
    get: (quizId) => apiClient.get(`/quiz/${quizId}/`),
    submit: (quizId, answers) =>
      apiClient.post("/quiz/submit/", {
        quiz_id: quizId,
        answers,
      }),
    history: () => apiClient.get("/quiz/history/"),
  },

  // Personalized Study Planner
  studyPlan: {
    getLatest: () => apiClient.get("/study-plan/"),
    generate: (params = {}) => apiClient.post("/study-plan/generate/", params),
    history: () => apiClient.get("/study-plan/history/"),
    get: (planId) => apiClient.get(`/study-plan/${planId}/`),
    delete: (planId) => apiClient.delete(`/study-plan/${planId}/`),
    toggleTask: (planId, taskIndex) =>
      apiClient.post(`/study-plan/${planId}/toggle-task/`, {
        task_index: taskIndex,
      }),
  },

  // Classical ML Topic Classifier
  classifier: {
    predict: (text) => apiClient.post("/classifier/predict/", { text }),
    status: () => apiClient.get("/classifier/status/"),
  },

  // Progress Analytics
  progress: {
    getSummary: () => apiClient.get("/progress/"),
  },

  // Health Check
  health: {
    check: () => apiClient.get("/health/"),
  },
};

export default apiClient;
