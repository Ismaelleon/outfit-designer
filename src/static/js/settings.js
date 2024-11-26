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
		document.cookie = "dark-mode=true";
	} else {
		document.cookie = "dark-mode=\"\"";
	}
}

switchEl.addEventListener('change', toggleDarkMode);
