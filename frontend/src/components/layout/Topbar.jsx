import { useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import Button from "../ui/Button";

export default function Topbar({ title }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <header className="flex items-center justify-between border-b border-line bg-void/60 px-6 py-4 backdrop-blur-sm">
      <h1 className="font-display text-lg font-semibold text-text-hi">{title}</h1>
      <div className="flex items-center gap-4">
        <span className="hidden font-mono text-xs text-text-mid sm:inline">{user?.email}</span>
        <Button variant="secondary" onClick={handleLogout}>
          Log out
        </Button>
      </div>
    </header>
  );
}
