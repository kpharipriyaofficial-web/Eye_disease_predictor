import { Link } from "react-router-dom";
import Button from "../ui/Button";
import { useAuth } from "../../hooks/useAuth";

export default function PublicNav() {
  const { isAuthenticated } = useAuth();

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-void/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2 font-display text-lg font-semibold">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-accent-cyan to-accent-blue text-void">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7-10-7-10-7Z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
          </span>
          Eye_ML
        </Link>
        <nav className="flex items-center gap-3">
          {isAuthenticated ? (
            <Button as={Link} to="/dashboard" variant="primary">
              Go to dashboard
            </Button>
          ) : (
            <>
              <Button as={Link} to="/login" variant="ghost">
                Log in
              </Button>
              <Button as={Link} to="/register" variant="primary">
                Get started
              </Button>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
