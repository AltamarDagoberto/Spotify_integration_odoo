document.addEventListener('DOMContentLoaded', function () {
  const filter = document.getElementById('filter');
  const pokemonList = document.getElementById('pokemon-list');
  const cards = pokemonList.querySelectorAll('.card');

  filter.addEventListener('change', function () {
    const selectedType = filter.value;

    cards.forEach(card => {
      const types = Array.from(card.querySelectorAll('.badge')).map(el => el.textContent);

      if (selectedType === 'All' || types.includes(selectedType)) {
        card.parentElement.style.display = '';
      } else {
        card.parentElement.style.display = 'none';
      }
    });
  });
});
