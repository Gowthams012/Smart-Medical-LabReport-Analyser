import { createContext, useCallback, useContext, useMemo, useState } from "react";
import apiClient from "../lib/apiClient";

const AuthContext = createContext(null);
const STORAGE_KEYS = {
  user: "labmate-user",
  token: "labmate-token",
};

const readStoredState = () => {
  try {
    const user = JSON.parse(localStorage.getItem(STORAGE_KEYS.user) || "null");
    const token = localStorage.getItem(STORAGE_KEYS.token);
    return { user, token };
  } catch (error) {
    console.warn("Unable to parse stored auth state", error);
    return { user: null, token: null };
  }
};

export const AuthProvider = ({ children }) => {
  const [{ user, token }, setAuthState] = useState(() => readStoredState());
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [authError, setAuthError] = useState(null);

  const persistAuth = useCallback((profile) => {
    if (!profile || !profile.token) return;
    setAuthState({ user: profile, token: profile.token });
    localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(profile));
    localStorage.setItem(STORAGE_KEYS.token, profile.token);
  }, []);

  const clearAuth = useCallback(() => {
    setAuthState({ user: null, token: null });
    localStorage.removeItem(STORAGE_KEYS.user);
    localStorage.removeItem(STORAGE_KEYS.token);
  }, []);

  const requestWrapper = useCallback(async (requestFn) => {
    setIsSubmitting(true);
    setAuthError(null);
    try {
      const response = await requestFn();
      return response;
    } catch (error) {
      const message = error.response?.data?.message || "Something went wrong";
      setAuthError(message);
      throw new Error(message);
    } finally {
      setIsSubmitting(false);
    }
  }, []);

  const login = useCallback(
    (credentials) =>
      requestWrapper(async () => {
        const { data } = await apiClient.post("/auth/login", credentials);
        persistAuth(data.data);
        return data;
      }),
    [persistAuth, requestWrapper]
  );

  const signup = useCallback(
    (payload) =>
      requestWrapper(async () => {
        const { data } = await apiClient.post("/auth/signup", payload);
        persistAuth(data.data);
        return data;
      }),
    [persistAuth, requestWrapper]
  );

  const googleLogin = useCallback(
    (googlePayload) =>
      requestWrapper(async () => {
        const { data } = await apiClient.post("/auth/google", googlePayload);
        persistAuth(data.data);
        return data;
      }),
    [persistAuth, requestWrapper]
  );

  const logout = useCallback(
    () =>
      requestWrapper(async () => {
        try {
          await apiClient.post("/auth/logout");
        } finally {
          clearAuth();
        }
      }),
    [clearAuth, requestWrapper]
  );

  const value = useMemo(
    () => ({
      user,
      token,
      isSubmitting,
      authError,
      login,
      signup,
      googleLogin,
      logout,
      clearAuthError: () => setAuthError(null),
    }),
    [authError, googleLogin, isSubmitting, login, logout, signup, token, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
