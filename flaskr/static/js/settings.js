const switchEl = document.querySelector("#dark-mode-switch input");

function setDarkModeSwitch() {
	if (document.cookie.includes("dark-mode=true")) {
		switchEl.checked = true;
	}
}

window.onload = setDarkModeSwitch;

function toggleDarkMode() {
	let documentEl = document.documentElement;
	documentEl.classList.toggle("dark");

	if (documentEl.classList[0] === "dark") {
		document.cookie = "dark-mode=true; path=/";
		document
			.querySelector('meta[name="theme-color"]')
			.setAttribute("content", "#18181b");
	} else {
		document.cookie = 'dark-mode=""; path=/';
		document
			.querySelector('meta[name="theme-color"]')
			.setAttribute("content", "#ffffff");
	}
}

switchEl.addEventListener("change", toggleDarkMode);

function showDeletionModal(event) {
	const deletionModal = document.getElementById("deletion-modal");

	// Show deletion modal
	deletionModal.classList.remove("hidden");
}

function hideDeletionModal(event) {
	event.preventDefault();

	const deletionModal = document.getElementById("deletion-modal");
	deletionModal.classList.add("hidden");
}
