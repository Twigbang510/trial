import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";
import { ThemeProvider } from "@/components/theme-provider.tsx";
import { authService } from "./services/auth";

// Initialize auth service to clean up any corrupted data
authService.init();

createRoot(document.getElementById("root")!).render(
  <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme" >
    <App />
  </ThemeProvider>
);
