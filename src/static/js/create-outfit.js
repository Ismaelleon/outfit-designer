// Show dialog on button click
const clothesDialog = document.getElementById('clothes-dialog');

function toggleOutfitDialog () {
	// Show dialog
	clothesDialog.classList.toggle('hidden');
}

// Select clothes menu functionality
const clothesEls = document.querySelectorAll('#clothes-dialog > section > section > section');
let selectedClothes = [];

function toggleSelected (event) {
	// Change background color
	event.target.lastElementChild.classList.toggle('hidden');

	// If clothes already in the list, remove them from the list
	for (let i = 0; i < selectedClothes.length; i++) {
		if (event.target.id === selectedClothes[i]) {
			selectedClothes.splice(i, 1);
			return false
		}
	}
	
	// Add clothes to the list
	selectedClothes.push(event.target.id);
}

for (let clothesEl of clothesEls) {
	clothesEl.addEventListener('click', toggleSelected);
}

// Save clothes
const addClothesButton = document.getElementById('add-clothes');
const clothesList = document.querySelector('#clothes-list');
const saveButton = document.querySelector('#clothes-dialog > section > button:nth-child(4)');
function saveOutfitClothes () {
	// Hide dialog
	toggleOutfitDialog();

	// Render selected clothes
	renderSelectedClothes();
}

function renderSelectedClothes () {
	let clothesListInnerHTML = '';

	// Append clothes image list
	for (let id of selectedClothes) {
		const clothesEl = document.getElementById(id);
		clothesListInnerHTML += `
			<p class="hidden">
				<input type="checkbox" name="clothes" id="${id}" value="${id}" checked />
			</p>
			<section class="flex items-center rounded border aspect-[3/4] relative border-zinc-200 dark:border-zinc-600 p-2" id="${id}">
				<button class="absolute top-0 right-0 p-2 bg-transparent border-transparent" onclick="removeClothes(event)" type="button">
					<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5">
						<path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
					</svg>

				</button>
				<img src="${clothesEl.firstElementChild.src}" />
			</section>
		`;
	}

	// Add "add clothes" button at the end
	clothesListInnerHTML += addClothesButton.outerHTML;
	
	// Replace html
	clothesList.innerHTML = clothesListInnerHTML;	
}

function removeClothes (event) {
	let clothingItemId = event.target.parentElement.id;

	// If clothing item id is in the list, remove it 
	for (let i = 0; i < selectedClothes.length; i++) {
		if (clothingItemId === selectedClothes[i]) {
			selectedClothes.splice(i, 1);
		}
	}

	renderSelectedClothes();
}

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
