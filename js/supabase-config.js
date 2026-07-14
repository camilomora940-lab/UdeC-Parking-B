// js/supabase-config.js

const SUPABASE_URL = 'https://mvqiqxelegizocmqphgd.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12cWlxeGVsZWdpem9jbXFwaGdkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM5Njk0ODgsImV4cCI6MjA5OTU0NTQ4OH0.d9245e7bm6mwt9Rt_pNAD1gcrhKQOWogjF4wZsrhdGs';

// Initialize Supabase Client
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
