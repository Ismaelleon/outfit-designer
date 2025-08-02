/** @type {import('tailwindcss').Config} */
module.exports = {
	content: [
		"../../views/*.html",
		"../../views/components/*.html",
		"../js/*.js",
	],
	darkMode: "selector",
	theme: {
		fontFamily: {
			sans: ["Geist"],
		},
		extend: {},
	},
	plugins: [],
};
