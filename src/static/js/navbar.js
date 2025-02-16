function toggleNavbarMenu() {
	document.getElementById("menu").classList.toggle("hidden");
	document.getElementById("menu").classList.toggle("flex");
}

document
	.getElementById("menu-open")
	.addEventListener("click", toggleNavbarMenu);
document
	.getElementById("menu-close")
	.addEventListener("click", toggleNavbarMenu);
