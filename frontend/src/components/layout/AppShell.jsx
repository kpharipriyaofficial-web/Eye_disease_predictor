import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

const TITLES = {
  "/dashboard": "Analyze",
  "/history": "Prediction history",
  "/profile": "Profile",
};

export default function AppShell() {
  const location = useLocation();
  const title = TITLES[location.pathname] || "Eye_ML";

  return (
    <div className="flex min-h-screen bg-void">
      <Sidebar />
      <div className="flex min-h-screen flex-1 flex-col">
        <Topbar title={title} />
        <main className="flex-1 px-6 py-8">
          <div className="mx-auto max-w-5xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
