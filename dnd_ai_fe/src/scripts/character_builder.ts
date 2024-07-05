export function renderCharacterBuilder() {
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
      mainContent.innerHTML = `
        <section id="character-builder">
          <h2>Character Builder</h2>
          <!-- Add your character builder content here -->
        </section>
      `;
    }
  }

  // async function loadEntityLikeTypeDropdown() {
//     // Assuming you have a dropdown element defined in your HTML with id "entityTypeDropdown"
//   const entityTypeDropdown = document.getElementById('entityTypeDropdown') as HTMLSelectElement;

//   // Define the options
//   const options = ['Entity', 'NPC', 'Player'];

//   // Populate the dropdown using populateAppendDropdown function
//   options.forEach(option => {
//     const optionElement = document.createElement('option');
//     optionElement.value = option.toLowerCase(); // You can set the value to lowercase if needed
//     optionElement.text = option;
//     entityTypeDropdown.add(optionElement);
//   });

//   populateAppendDropdown(entityTypeDropdown, options, '')
// }