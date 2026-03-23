import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { getRootElement } from "./lib/dom";
import "./index.css";

const rootElement = getRootElement();

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
