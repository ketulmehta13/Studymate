import React, { createContext, useContext, useState, useEffect } from "react";
import { api } from "../services/api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("studymate_user");
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() =>
    localStorage.getItem("studymate_access_token")
  );
  const [isLoading, setIsLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  useEffect(() => {
    const verifyUser = async () => {
      const storedToken = localStorage.getItem("studymate_access_token");
      if (!storedToken) {
        setIsLoading(false);
        return;
      }
      try {
        const res = await api.auth.me();
        setUser(res.data);
        localStorage.setItem("studymate_user", JSON.stringify(res.data));
      } catch (err) {
        logout();
      } finally {
        setIsLoading(false);
      }
    };

    verifyUser();

    const handleLogoutEvent = () => logout();
    window.addEventListener("auth_logout", handleLogoutEvent);
    return () => window.removeEventListener("auth_logout", handleLogoutEvent);
  }, []);

  const login = async (identifier, password) => {
    setAuthError(null);
    try {
      const res = await api.auth.login(identifier, password);
      const { access, refresh, user: userData } = res.data;

      localStorage.setItem("studymate_access_token", access);
      localStorage.setItem("studymate_refresh_token", refresh);
      localStorage.setItem("studymate_user", JSON.stringify(userData));

      setToken(access);
      setUser(userData);
      return { success: true };
    } catch (err) {
      const msg =
        err.response?.data?.message ||
        err.response?.data?.details?.detail ||
        "Invalid username or password.";
      setAuthError(msg);
      return { success: false, error: msg };
    }
  };

  const register = async (username, email, password) => {
    setAuthError(null);
    try {
      await api.auth.register(username, email, password);
      // Automatically log in after registration
      return await login(username, password);
    } catch (err) {
      const msg =
        err.response?.data?.message ||
        "Registration failed. Please check your details.";
      setAuthError(msg);
      return { success: false, error: msg };
    }
  };

  const logout = () => {
    localStorage.removeItem("studymate_access_token");
    localStorage.removeItem("studymate_refresh_token");
    localStorage.removeItem("studymate_user");
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user && !!token,
        isLoading,
        authError,
        setAuthError,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
