  const themes = {
    'darkly': 'https://bootswatch.com/5/darkly/bootstrap.min.css',
    'flatly': 'https://bootswatch.com/5/flatly/bootstrap.min.css'
  };

  function applyTheme(themeName) {
    const link = document.getElementById('theme-style');
    link.href = themes[themeName];
    localStorage.setItem('selectedTheme', themeName);

    // Actualiza el valor seleccionado en el menú
    const select = document.getElementById('theme-select');
    if (select) {
      select.value = themeName;
    }
  }

  // Al cargar la página
  document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('selectedTheme') || 'flatly';
    applyTheme(savedTheme);

    // Manejar cambio de tema desde el menú
    document.getElementById('theme-select').addEventListener('change', (e) => {
      applyTheme(e.target.value);
    });
  });