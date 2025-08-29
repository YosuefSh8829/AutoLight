import React, { useState } from "react";
import { supabase } from "../supabaseClient";

export default function Signup() {
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setMessage("");
    setLoading(true);

    try {
      // 🔹 Step 1: Create user in Supabase Auth
      const { data, error } = await supabase.auth.signUp({
        email: form.email,
        password: form.password,
      });

      if (error) throw error;

      // 🔹 Step 2: Insert into your custom "users" table
      if (data.user) {
        const { error: insertError } = await supabase.from("users").insert([
          {
            uuid: data.user.id,
            email: form.email,
            user_name: form.name,
            created_at: new Date(),
          },
        ]);

        if (insertError) throw insertError;

        setMessage(
          "🎉 Account created! Please check your email to confirm before logging in."
        );
        setForm({ name: "", email: "", password: "" }); // clear form
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-container fade-in">
      <div className="auth-box slide-up">
        <h2 className="form-title">Create Account</h2>

        <form onSubmit={handleSubmit} className="form">
          <input
            type="text"
            placeholder="Full Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
            className="form-input"
          />
          <input
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            required
            className="form-input"
          />
          <input
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            required
            className="form-input"
          />

          <button
            type="submit"
            className={`auth-btn ${loading ? "loading" : ""}`}
            disabled={loading}
          >
            {loading ? "Signing Up..." : "Sign Up"}
          </button>
        </form>

        {error && <p className="error-text shake">❌ {error}</p>}
        {message && <p className="success-text bounce-in">{message}</p>}
      </div>
    </div>
  );
}
