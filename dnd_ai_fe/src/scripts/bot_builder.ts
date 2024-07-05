

  export function renderBotBuilder() {
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
      mainContent.innerHTML = `
        <section id="bot-builder">
          <h2>Bot Builder</h2>
          <!-- Add your bot builder content here -->
        </section>
      `;
    }
  }

  