    const themes = {
      'cyborg': 'https://bootswatch.com/5/cyborg/bootstrap.min.css',
      'flatly': 'https://bootswatch.com/5/flatly/bootstrap.min.css'
    };

    function applyTheme(themeName) {
      const link = document.getElementById('theme-style');
      link.href = themes[themeName] || themes['flatly'];
      localStorage.setItem('selectedTheme', themeName);
    }

    // Al cargar la página
    const savedTheme = localStorage.getItem('selectedTheme') || 'flatly';
    applyTheme(savedTheme);

    // Botón para alternar tema
    document.addEventListener('DOMContentLoaded', () => {
      document.getElementById('toggle-theme').addEventListener('click', () => {
        const currentTheme = localStorage.getItem('selectedTheme') || 'flatly';
        const newTheme = currentTheme === 'cyborg' ? 'flatly' : 'cyborg';
        applyTheme(newTheme);
      });
    });