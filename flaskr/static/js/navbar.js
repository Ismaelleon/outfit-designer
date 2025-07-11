function showLoadingBar() {
	document.getElementById("loading-bar").classList.add("htmx-request");
}

window.addEventListener("DOMContentLoaded", () => {
	let navbarLinks = document.querySelectorAll("#menu a");
	navbarLinks.forEach((link) =>
		link.addEventListener("click", showLoadingBar)
	);

	let mobileNavbarLinks = document.querySelectorAll("#mobile-menu a");
	mobileNavbarLinks.forEach((link) =>
		link.addEventListener("click", showLoadingBar)
	);
});
