/* =====================================================
   UdeC ParkApp — Auth Module (Supabase)
   ===================================================== */

const AuthModule = (() => {
  async function login(email, password, role) {
    // We try to sign in. If the user doesn't exist, we sign them up automatically for this demo.
    let { data, error } = await supabase.auth.signInWithPassword({
      email: email,
      password: password
    });

    if (error && error.message.includes('Invalid login credentials')) {
      // Auto sign-up for the sake of the prototype if user doesn't exist
      const { data: signUpData, error: signUpError } = await supabase.auth.signUp({
        email: email,
        password: password,
        options: {
          data: {
            role: role,
            name: email.split('@')[0],
          }
        }
      });
      if (signUpError) {
        throw signUpError;
      }
      data = signUpData;
    } else if (error) {
      throw error;
    }

    return getSession();
  }

  async function setDemoUser() {
    const email = `demo_${Math.floor(Math.random()*10000)}@udec.cl`;
    await supabase.auth.signUp({
      email: email,
      password: 'demo_password',
      options: { data: { role: 'staff', name: 'Usuario Demo' } }
    });
    return getSession();
  }

  async function getSession() {
    const { data, error } = await supabase.auth.getSession();
    if (error || !data.session) return null;
    
    const user = data.session.user;
    const namePart = user.email.split('@')[0];
    const names = namePart.split('.');
    const formattedName = user.user_metadata?.name || names.map(n => n.charAt(0).toUpperCase() + n.slice(1)).join(' ');

    return {
      email: user.email,
      name: formattedName,
      role: user.user_metadata?.role || 'student',
      initials: formattedName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0,2),
      faculty: user.user_metadata?.role === 'student' ? 'Estudiante UdeC' : 'Funcionario UdeC',
      vehicles: [],
      loginTime: new Date(data.session.user.last_sign_in_at).getTime()
    };
  }

  async function isLoggedIn() {
    const session = await getSession();
    return session !== null;
  }

  async function logout() {
    await supabase.auth.signOut();
  }

  async function requireAuth() {
    const session = await getSession();
    if (!session) {
      window.location.href = 'index.html';
      return null;
    }
    return session;
  }

  function updateVehicles(vehicles) {
    // Mock updating vehicles in metadata or database for now
    console.log("Updating vehicles", vehicles);
  }

  return {
    login,
    logout,
    isLoggedIn,
    getSession,
    requireAuth,
    updateVehicles,
    setDemoUser
  };
})();
