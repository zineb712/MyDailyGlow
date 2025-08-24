document.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
    // Charger l'état sauvegardé
    const saved = localStorage.getItem(checkbox.id);
    if (saved === 'true') {
        checkbox.checked = true;
    }

    // Sauvegarder quand on clique
    checkbox.addEventListener('change', () => {
        localStorage.setItem(checkbox.id, checkbox.checked);
    });
});
