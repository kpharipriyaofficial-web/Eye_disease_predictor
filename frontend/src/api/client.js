import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_BASE_URL) {
  // Fails loud in dev rather than silently hitting a wrong/empty base URL.
  // eslint-disable-next-line no-console
  console.warn(
    "VITE_API_BASE_URL is not set. Create a .env file — see .env.example."
  );
}

export const TOKEN_KEY = "eyeml_token";

const client = axios.create({
  baseURL: API_BASE_URL,
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY);
      if (
        typeof window !== "undefined" &&
        window.location.pathname !== "/login"
      ) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

/**
 * Extracts a human-readable message from a FastAPI error response
 * (handles the 422 HTTPValidationError shape and plain {detail} errors)
 * without ever leaking a raw stack trace to the UI.
 */
export function getErrorMessage(error, fallback = "Something went wrong. Please try again.") {
  const detail = error?.response?.data?.detail;
  if (!detail) return error?.message || fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => d.msg).filter(Boolean).join(" ") || fallback;
  }
  return fallback;
}

export default client;
