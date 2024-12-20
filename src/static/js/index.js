const logInButton = document.getElementById('log-in'),
	signUpButton = document.getElementById('sign-up'),
	getStartedButton = document.getElementById('get-started'),
	joinButton = document.getElementById('join');

const signUpToggleLink = document.getElementById('signup-toggle'),
	logInToggleLink = document.getElementById('login-toggle');

const logInDialog = document.getElementById('login-dialog'),
	signUpDialog = document.getElementById('signup-dialog');

const closeButtons = document.querySelectorAll('.close');

function toggleDialog (dialog) {
	if (dialog === 'log-in') {
		signUpDialog.classList.add('hidden');
		logInDialog.classList.remove('hidden');
	} else if (dialog === 'sign-up') {
		logInDialog.classList.add('hidden');
		signUpDialog.classList.remove('hidden');
	} else if (dialog === 'all') {
		logInDialog.classList.add('hidden');
		signUpDialog.classList.add('hidden');
	}
}

logInButton.addEventListener('click', () => toggleDialog('log-in'));
signUpButton.addEventListener('click', () => toggleDialog('sign-up'))
joinButton.addEventListener('click', () => toggleDialog('sign-up'))
getStartedButton.addEventListener('click', () => toggleDialog('sign-up'))
signUpToggleLink.addEventListener('click', () => toggleDialog('sign-up'));
logInToggleLink.addEventListener('click', () => toggleDialog('log-in'));
closeButtons.forEach(el => el.addEventListener('click', () => toggleDialog('all')))

function toggleMenu () {
	document.getElementById('menu').classList.toggle('hidden');
	document.getElementById('menu').classList.toggle('flex');
}

document.getElementById('menu-open').addEventListener('click', toggleMenu);
document.getElementById('menu-close').addEventListener('click', toggleMenu);
for (const el of document.querySelectorAll('#menu > a')) {
	el.addEventListener('click', toggleMenu);
}
