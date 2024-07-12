function toggleMenu () {
	document.getElementById('menu').classList.toggle('hidden');
	document.getElementById('menu').classList.toggle('flex');
}

document.getElementById('menu-open').addEventListener('click', toggleMenu);
document.getElementById('menu-close').addEventListener('click', toggleMenu);
