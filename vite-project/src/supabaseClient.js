import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = "https://wczwmlhzsousesecnvnu.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndjendtbGh6c291c2VzZWNudm51Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY0MTg0OTEsImV4cCI6MjA3MTk5NDQ5MX0.McW3rnjF6eY1WLO41Tqd7f8ePjazvLHkBhl5r2pMMq4"; // ⚠️ use anon key, not service_role

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);