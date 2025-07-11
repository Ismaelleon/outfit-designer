const logInButton = document.getElementById("log-in"),
	signUpButton = document.getElementById("sign-up"),
	getStartedButton = document.getElementById("get-started");

const signUpToggleLink = document.getElementById("signup-toggle"),
	logInToggleLink = document.getElementById("login-toggle"),
	logInToggleLink2 = document.getElementById("join"),
	forgotPasswordToggleLink = document.getElementById(
		"forgot-password-toggle"
	);

const logInDialog = document.getElementById("login-dialog"),
	signUpDialog = document.getElementById("signup-dialog"),
	forgotPasswordDialog = document.getElementById("forgot-password-dialog");

const closeButtons = document.querySelectorAll(".close");

function toggleDialog(dialog) {
	if (dialog === "log-in") {
		signUpDialog.classList.add("hidden");
		logInDialog.classList.remove("hidden");
		forgotPasswordDialog.classList.add("hidden");
	} else if (dialog === "sign-up") {
		signUpDialog.classList.remove("hidden");
		logInDialog.classList.add("hidden");
		forgotPasswordDialog.classList.add("hidden");
	} else if (dialog === "forgot-password") {
		signUpDialog.classList.add("hidden");
		logInDialog.classList.add("hidden");
		forgotPasswordDialog.classList.remove("hidden");
	} else if (dialog === "all") {
		signUpDialog.classList.add("hidden");
		logInDialog.classList.add("hidden");
		forgotPasswordDialog.classList.add("hidden");
	}
}

logInButton.addEventListener("click", () => toggleDialog("log-in"));
signUpButton.addEventListener("click", () => toggleDialog("sign-up"));
getStartedButton.addEventListener("click", () => toggleDialog("sign-up"));
signUpToggleLink.addEventListener("click", () => toggleDialog("sign-up"));
logInToggleLink.addEventListener("click", () => toggleDialog("log-in"));
logInToggleLink2.addEventListener("click", () => toggleDialog("log-in"));
forgotPasswordToggleLink.addEventListener("click", () =>
	toggleDialog("forgot-password")
);
closeButtons.forEach((el) =>
	el.addEventListener("click", () => toggleDialog("all"))
);

function toggleMenu() {
	document.getElementById("menu").classList.toggle("hidden");
	document.getElementById("menu").classList.toggle("flex");
}

document.getElementById("menu-open").addEventListener("click", toggleMenu);
document.getElementById("menu-close").addEventListener("click", toggleMenu);
for (const el of document.querySelectorAll("#menu > a")) {
	el.addEventListener("click", toggleMenu);
}
