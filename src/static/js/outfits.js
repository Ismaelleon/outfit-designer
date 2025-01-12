function toggleMenu(event) {
	event.currentTarget.querySelector("ul").classList.toggle("hidden");
}

function toggleFiltersMenu(event) {
	document.getElementById("filters-menu").classList.toggle("hidden");
	event.currentTarget.classList.toggle("bg-zinc-200 dark:bg-zinc-800");
}

function hideDeletionModal() {
	const deletionModal = document.getElementById("deletion-modal");
	deletionModal.classList.add("hidden");
}

function showDeletionModal(event) {
	const deletionModal = document.getElementById("deletion-modal");
	const outfitEl = event.target.closest("section");
	const deleteButton = deletionModal.firstElementChild.children[1];

	// Show deletion modal
	deletionModal.classList.remove("hidden");

	// Set the attribute to use the DELETE method, with the outfit id
	deleteButton.setAttribute("hx-delete", `/outfits/delete/${outfitEl.id}`);

	// Set the target for htmx swap to #outfits-list
	deleteButton.setAttribute("hx-target", "#outfits-list");

	// Make htmx process the button
	htmx.process(deleteButton);
}
