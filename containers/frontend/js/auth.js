

document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;
  
    const res = await fetch(`${BASE_URLS.auth}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
  
    const data = await res.json();
    if (res.ok) {
      localStorage.setItem("token", data.access_token);
      alert("Login successful");
      window.location.href = "products.html";
    } else {
      alert(data.message || "Login failed");
    }
  });
  
document.getElementById("register-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("register-username").value;
    const password = document.getElementById("register-password").value;
  
    const res = await fetch(`${BASE_URLS.auth}/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": "registration-secret-key"  
      },
      body: JSON.stringify({ username, password })
    });
  
    const data = await res.json();
    if (res.ok) {
      alert("Registration successful");
    } else {
      alert(data.message || "Registration failed");
    }
  });
