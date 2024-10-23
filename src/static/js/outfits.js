function toggleMenu(event) {
	event.currentTarget.querySelector("ul").classList.toggle("hidden");
}

function toggleFiltersMenu(event) {
	document.getElementById("filters-menu").classList.toggle("hidden");
	event.currentTarget.classList.toggle("bg-zinc-200 dark:bg-zinc-800");
}
