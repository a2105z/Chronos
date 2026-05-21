import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import App from "./App";
import AuthScreen from "./components/auth/AuthScreen";
import { AuthProvider } from "./auth/AuthContext";
import { getRootElement } from "./lib/dom";
import "./index.css";

ReactDOM.createRoot(getRootElement()).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<AuthScreen />} />
          <Route path="/app/*" element={<App />} />
          <Route path="/" element={<Navigate to="/app" replace />} />
          <Route path="*" element={<Navigate to="/app" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
