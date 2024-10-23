function toggleDarkMode() {
	let documentEl = document.documentElement;
	documentEl.classList.toggle("dark");

	if (documentEl.classList[0] === "dark") {
		document.cookie = "dark-mode=true";
	} else {
		document.cookie = "";
	}
}

document.querySelector('#dark-mode-switch input').addEventListener('change', toggleDarkMode);
