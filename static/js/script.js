document.addEventListener('DOMContentLoaded', function() {
  const body = document.querySelector("body"),
        sidebar = body.querySelector(".sidebar"),
        toggle = body.querySelector(".toggle"),
        searchBtn = body.querySelector(".search-box"),
        modeSwitch = body.querySelector(".toggle-switch"),
        modeText = body.querySelector(".mode-text");
        
  // Check if dark mode preference is stored in localStorage
  const isDarkMode = localStorage.getItem('darkMode') === 'true';

  // Set initial state based on localStorage or default to dark mode
  if (isDarkMode) {
      enableDarkMode();
      modeText.innerText = "Light Mode";
  } else {
      disableDarkMode();
      modeText.innerText = "Dark Mode";
  }

  toggle.addEventListener("click", () =>{
      sidebar.classList.toggle("close");
  });
  
  searchBtn.addEventListener("click", () =>{
      sidebar.classList.remove("close");
  });

  modeSwitch.addEventListener("click", () =>{
      body.classList.toggle("dark");
      const isDarkMode = body.classList.contains("dark");

      if(isDarkMode){
          modeText.innerText = "Light Mode";
          localStorage.setItem('darkMode', 'true');
      } else {
          modeText.innerText = "Dark Mode";
          localStorage.setItem('darkMode', 'false');
      }
  });

  // Function to enable dark mode
  function enableDarkMode() {
      body.classList.add("dark");
  }
  
  // Function to disable dark mode
  function disableDarkMode() {
      body.classList.remove("dark");
  }
});
