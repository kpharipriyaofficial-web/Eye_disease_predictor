import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import PublicNav from "../components/layout/PublicNav";
import Card from "../components/ui/Card";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";
import { useAuth } from "../hooks/useAuth";

export default function Register() {
  const { signup } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({ email: "", password: "", confirm: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function update(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    // Mirrors SignupRequest constraints from openapi.json exactly.
    if (form.email.length < 3 || form.email.length > 254) {
      setError("Enter a valid email address.");
      return;
    }
    if (form.password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (form.password.length > 128) {
      setError("Password must be at most 128 characters.");
      return;
    }
    if (form.password !== form.confirm) {
      setError("Passwords do not match.");
      return;
    }

    setSubmitting(true);
    try {
      await signup({ email: form.email, password: form.password });
      navigate("/dashboard", { replace: true });
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
          <h1 className="mb-1 font-display text-xl font-semibold">Create your account</h1>
          <p className="mb-6 text-sm text-text-mid">Start analyzing eye images with Eye_ML.</p>

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
              autoComplete="new-password"
              minLength={8}
              maxLength={128}
              value={form.password}
              onChange={update("password")}
              placeholder="At least 8 characters"
              required
            />
            <Input
              id="confirm"
              label="Confirm password"
              type="password"
              autoComplete="new-password"
              maxLength={128}
              value={form.confirm}
              onChange={update("confirm")}
              placeholder="Re-enter your password"
              required
            />
            {error && <p className="text-xs text-signal-red">{error}</p>}
            <Button type="submit" variant="primary" loading={submitting} className="mt-2">
              Create account
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-text-mid">
            Already have an account?{" "}
            <Link to="/login" className="text-accent-cyan hover:underline">
              Log in
            </Link>
          </p>
        </Card>
      </div>
    </div>
  );
}
