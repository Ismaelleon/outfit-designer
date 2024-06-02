// Toggle outfit menu
const outfitsEls = document.querySelectorAll('#clothing-list > section > header > button');

function toggleMenu (event) {
	event.currentTarget.querySelector('ul').classList.toggle('hidden');
}

for (let outfitEl of outfitsEls) {
	outfitEl.addEventListener('click', toggleMenu)
}
