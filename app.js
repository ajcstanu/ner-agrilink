// app.js — Main application logic for NER AgroLink
// Connects frontend to the Flask REST API (http://localhost:5000)

const API_BASE = "http://localhost:5000/api";

function toggleMenu() {
  document.querySelector(".nav-links").classList.toggle("open");
}

async function submitBooking(e) {
  e.preventDefault();
  const form = e.target;
  const fields = form.querySelectorAll("input, select, textarea");

  const payload = {
    farmer_name:    form.querySelector("input[placeholder='Your full name']")?.value,
    phone:          form.querySelector("input[type='tel']")?.value,
    village:        form.querySelectorAll("input[type='text']")[1]?.value,
    produce:        form.querySelectorAll("select")[0]?.value?.toLowerCase().split(" ")[0],
    weight_kg:      parseFloat(form.querySelector("input[type='number']")?.value) || 0,
    pickup_date:    form.querySelector("input[type='date']")?.value,
    transport_mode: form.querySelectorAll("select")[1]?.value,
  };

  form.style.opacity = "0.5";
  form.style.pointerEvents = "none";

  try {
    const res  = await fetch(`${API_BASE}/booking`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload),
    });
    const data = await res.json();
    form.style.display = "none";
    const success = document.getElementById("booking-success");
    success.style.display = "block";
    success.textContent = `✅ ${data.message} (ID: ${data.booking_id})`;
  } catch (err) {
    form.style.opacity = "1";
    form.style.pointerEvents = "auto";
    alert("Booking failed. Make sure the backend server is running.");
  }
}

// Smooth reveal on scroll
document.addEventListener("DOMContentLoaded", () => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll(".solution-card, .benefit-card, .dash-stat").forEach(el => {
    el.style.opacity = "0";
    el.style.transform = "translateY(24px)";
    el.style.transition = "opacity 0.5s ease, transform 0.5s ease";
    observer.observe(el);
  });

  // Active nav link on scroll
  const sections = document.querySelectorAll("section[id]");
  const navLinks = document.querySelectorAll(".nav-links a");
  window.addEventListener("scroll", () => {
    let current = "";
    sections.forEach(s => {
      if (window.scrollY >= s.offsetTop - 120) current = s.getAttribute("id");
    });
    navLinks.forEach(link => {
      link.style.color = "";
      if (link.getAttribute("href") === "#" + current) link.style.color = "var(--gold)";
    });
  });
});
