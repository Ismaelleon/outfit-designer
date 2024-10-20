// Show image on input change
const imgPreviewContainer = document.getElementById('image-preview'),
	inputEl = document.getElementById('image-input'),
	inputLabelEl = document.querySelector('label[for="image-input"]'),
	imgEl = document.querySelector('#image-preview > img'),
	removePreviewButton = document.querySelector('#image-preview > button');

function setImage () {
	// Set image source
	imgEl.setAttribute('src', URL.createObjectURL(inputEl.files[0]));

	// Hide label for file input
	inputLabelEl.classList.add('hidden');

	// Show image preview
	imgPreviewContainer.classList.remove('hidden');

}

function removeImage (event) {
	// Prevent making a form request 
	event.preventDefault();

	// Remove image source
	imgEl.setAttribute('src', '');

	// Show label for file input
	inputLabelEl.classList.remove('hidden');

	// Hide image preview
	imgPreviewContainer.classList.add('hidden');
}

inputEl.addEventListener('change', setImage);
removePreviewButton.addEventListener('click', removeImage);
