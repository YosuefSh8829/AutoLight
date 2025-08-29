import React, { useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "./AuthContext";
import { supabase } from "../supabaseClient";

function Header() {
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  async function handleLogout() {
    await supabase.auth.signOut();
    navigate("/"); // ✅ go back to home after logout
  }

  return (
    <div className="parent flex justify-between items-center px-6 py-4 bg-gray-900 shadow-lg">
      <div>
        <p className="welcometext text-2xl font-bold text-white tracking-wide">
          AutoLight
        </p>
      </div>

      <div className="links flex gap-6 items-center text-white">
        <Link to="/" className="link hover:text-blue-400 transition-colors">
          Home
        </Link>

        {user && (
          <>
            <Link
              to="/dashboard"
              className="link hover:text-blue-400 transition-colors"
            >
              Dashboard
            </Link>
            <Link
              to="/Controlpanel"
              className="link hover:text-blue-400 transition-colors"
            >
              Control
            </Link>
          </>
        )}

        {!user ? (
          <>
            <Link
              to="/login"
              className="link hover:text-blue-400 transition-colors"
            >
              Login
            </Link>
            <Link
              to="/signup"
              className="link hover:text-blue-400 transition-colors"
            >
              Sign up
            </Link>
          </>
        ) : (
          <>
            <span className="link text-gray-300">👋 {user.email}</span>
            <button
              onClick={handleLogout}
              className="btn-logout relative px-4 py-2 rounded-lg bg-red-500 text-white font-semibold 
                shadow-md overflow-hidden 
                transition-all duration-300 
                hover:bg-red-600 hover:scale-105 active:scale-95"
            >
              <span className="relative z-10">Sign Out</span>
              <span className="absolute inset-0 bg-red-700 opacity-0 transition-opacity duration-300 hover:opacity-20"></span>
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default Header;
