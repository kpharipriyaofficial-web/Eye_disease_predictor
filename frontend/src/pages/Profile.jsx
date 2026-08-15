import { useNavigate } from "react-router-dom";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import { useAuth } from "../hooks/useAuth";
import { formatDate } from "../utils/formatters";

export default function Profile() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  if (!user) return null;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="font-display text-xl font-semibold text-text-hi">Profile</h2>
        <p className="mt-1 text-sm text-text-mid">Your account details.</p>
      </div>

      <Card className="max-w-md p-6">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-accent-cyan to-accent-blue font-display text-lg font-semibold text-void">
            {user.email.charAt(0).toUpperCase()}
          </div>
          <div>
            <p className="font-medium text-text-hi">{user.email}</p>
            <span
              className={`mt-1 inline-block rounded-full px-2 py-0.5 text-[11px] ${
                user.is_active
                  ? "bg-signal-green/10 text-signal-green"
                  : "bg-signal-red/10 text-signal-red"
              }`}
            >
              {user.is_active ? "Active" : "Inactive"}
            </span>
          </div>
        </div>

        <dl className="mt-6 space-y-3 border-t border-line pt-5 text-sm">
          <div className="flex justify-between">
            <dt className="text-text-mid">User ID</dt>
            <dd className="max-w-[60%] truncate font-mono text-text-hi">{user.id}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-text-mid">Member since</dt>
            <dd className="text-text-hi">{formatDate(user.created_at)}</dd>
          </div>
        </dl>

        <Button variant="danger" onClick={handleLogout} className="mt-6 w-full">
          Log out
        </Button>
      </Card>
    </div>
  );
}
