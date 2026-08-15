import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import PublicNav from "../components/layout/PublicNav";
import Card from "../components/ui/Card";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";
import { useAuth } from "../hooks/useAuth";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/dashboard";

  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function update(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (form.email.length < 3) {
      setError("Enter a valid email address.");
      return;
    }
    if (form.password.length < 1) {
      setError("Enter your password.");
      return;
    }

    setSubmitting(true);
    try {
      await login(form);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen">
      <PublicNav />
      <div className="flex min-h-[calc(100vh-73px)] items-center justify-center px-6 py-16">
        <Card className="w-full max-w-sm p-8">
          <h1 className="mb-1 font-display text-xl font-semibold">Welcome back</h1>
          <p className="mb-6 text-sm text-text-mid">Log in to continue to your dashboard.</p>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <Input
              id="email"
              label="Email"
              type="email"
              autoComplete="email"
              maxLength={254}
              value={form.email}
              onChange={update("email")}
              placeholder="you@example.com"
              required
            />
            <Input
              id="password"
              label="Password"
              type="password"
              autoComplete="current-password"
              maxLength={128}
              value={form.password}
              onChange={update("password")}
              placeholder="••••••••"
              required
            />
            {error && <p className="text-xs text-signal-red">{error}</p>}
            <Button type="submit" variant="primary" loading={submitting} className="mt-2">
              Log in
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-text-mid">
            Don't have an account?{" "}
            <Link to="/register" className="text-accent-cyan hover:underline">
              Create one
            </Link>
          </p>
        </Card>
      </div>
    </div>
  );
}
