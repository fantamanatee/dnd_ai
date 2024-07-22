import { renderHome } from "./home";
import { renderBotBuilder } from "./bot_builder";
import { renderCharacterBuilder } from "./character_builder";
import { clearAllSessionsOnPageExit } from "./util"; 

// Router function to handle navigation
function handleNavigation(event: Event) {
  event.preventDefault();
  const target = event.target as HTMLAnchorElement;
  const page = target.getAttribute("data-page");

  if (page === "home") {
    console.log('calling renderHome using handleNavigation')
    renderHome();
  } else if (page === "character-builder") {
    renderCharacterBuilder();
  } else if (page === "bot-builder") {
    renderBotBuilder();
  } else {
    console.error("Page not found");
  }
}


// Listen for link clicks in the navigation.
document.querySelectorAll("nav a").forEach((link) => {
  link.addEventListener("click", handleNavigation);
});

document.addEventListener('DOMContentLoaded', () => {
  renderHome();
  const themeToggle = document.getElementById("themeToggle");
  // Optionally, check for saved preference in localStorage
  if (localStorage.getItem("theme") === "dark") {
    document.body.classList.add("dark-mode");
  }

  themeToggle!.addEventListener("click", () => {
    const dark = document.body.classList.toggle("dark-mode");
    console.log("Theme toggle is now ", dark ? "dark" : "light");
    // Save preference to localStorage
    if (document.body.classList.contains("dark-mode")) {
      localStorage.setItem("theme", "dark");
    } else {
      localStorage.setItem("theme", "light");
    }
  });
});

clearAllSessionsOnPageExit();
