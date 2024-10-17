function toggleMenu(event) {
	event.stopPropagation();
	event.target.children[1].classList.toggle("hidden");
}

function toggleFiltersMenu() {
	document.getElementById("filters-menu").classList.toggle("hidden");
}
