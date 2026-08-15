import client from "./client";

/**
 * POST /auth/signup
 * Body: { email, password } -> 201 AuthResponse { access_token, token_type, user }
 */
export async function signup({ email, password }) {
  const { data } = await client.post("/auth/signup", { email, password });
  return data;
}

/**
 * POST /auth/login
 * Body: { email, password } -> 200 AuthResponse { access_token, token_type, user }
 */
export async function login({ email, password }) {
  const { data } = await client.post("/auth/login", { email, password });
  return data;
}

/**
 * GET /auth/me (Bearer required) -> UserResponse
 */
export async function getCurrentUser() {
  const { data } = await client.get("/auth/me");
  return data;
}
