import { create } from "zustand";

interface AuthStore {
  token: string | null;
  isAuthenticated: boolean;
  setToken: (token: string) => void;
  clearToken: () => void;
  initFromStorage: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  token: null,
  isAuthenticated: false,
  setToken: (token) => {
    if (typeof window !== "undefined") localStorage.setItem("access_token", token);
    set({ token, isAuthenticated: true });
  },
  clearToken: () => {
    if (typeof window !== "undefined") localStorage.removeItem("access_token");
    set({ token: null, isAuthenticated: false });
  },
  initFromStorage: () => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("access_token");
      if (token) set({ token, isAuthenticated: true });
    }
  },
}));
