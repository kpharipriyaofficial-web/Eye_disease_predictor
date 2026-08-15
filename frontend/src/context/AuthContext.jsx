import { createContext, useCallback, useEffect, useState } from "react";
import * as authApi from "../api/auth";
import { TOKEN_KEY, getErrorMessage } from "../api/client";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // true while we validate a stored token
  const [error, setError] = useState(null);

  // On first load: if a token exists, validate it against /auth/me.
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      setLoading(false);
      return;
    }
    authApi
      .getCurrentUser()
      .then((me) => setUser(me))
      .catch(() => {
        localStorage.removeItem(TOKEN_KEY);
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async ({ email, password }) => {
    setError(null);
    try {
      const res = await authApi.login({ email, password });
      localStorage.setItem(TOKEN_KEY, res.access_token);
      setUser(res.user);
      return res.user;
    } catch (err) {
      const message = getErrorMessage(err, "Invalid email or password.");
      setError(message);
      throw new Error(message);
    }
  }, []);

  const signup = useCallback(async ({ email, password }) => {
    setError(null);
    try {
      const res = await authApi.signup({ email, password });
      localStorage.setItem(TOKEN_KEY, res.access_token);
      setUser(res.user);
      return res.user;
    } catch (err) {
      const message = getErrorMessage(err, "Could not create your account.");
      setError(message);
      throw new Error(message);
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setUser(null);
  }, []);

  const value = {
    user,
    loading,
    error,
    isAuthenticated: !!user,
    login,
    signup,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
