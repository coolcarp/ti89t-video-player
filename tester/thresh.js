const canvas = document.querySelector('canvas');
const p = document.querySelector('p');

const size = 1; // 0.5
const fps = 10; // 30

canvas.width = 160 * size;
canvas.height = 100 * size;

const c = canvas.getContext('2d');

let currentEl

let defaultThresh = 128;
let threshold = defaultThresh;

function updateCanvas() {
	c.drawImage(currentEl, 0, 0);
	currentImgData = c.getImageData(0, 0, currentEl.width, currentEl.height)
	for(let i = 0; i < currentImgData.data.length; i+=4) {
		let r = currentImgData.data[i], g = currentImgData.data[i+1], b = currentImgData.data[i+2];
		let grey = .299 * r + .587 * g + .114 * b >= threshold ? 255 : 0;
		currentImgData.data[i] = grey;
		currentImgData.data[i+2] = grey;
		currentImgData.data[i+1] = grey;
	}
	c.putImageData(currentImgData, 0, 0);
}

let vid = document.createElement("video");
let img = document.createElement("img");

function showFile(input) { // Called by upload to file input
	let file = input.files[0];
	
	currentEl = file.name.includes(".mp4") || file.name.includes(".webm") ? vid : img;

	let reader = new FileReader();
	reader.readAsDataURL(file);
	
	img.onload = function() {
		canvas.width = img.width;
		canvas.height = img.height;
		threshold = defaultThresh;
		updateCanvas();
	}
	vid.onloadeddata = function() {
		vid.width = vid.videoWidth;
		vid.height = vid.videoHeight;
		vid.play();
		canvas.width = vid.videoWidth
		canvas.height = vid.videoHeight
		threshold = defaultThresh;
		function loop() {
			if(currentEl.src == reader.result) {
				updateCanvas();
				requestAnimationFrame(loop);
			}
		}
		requestAnimationFrame(loop);
	}
	reader.onload = function() {
		currentEl.src = reader.result
	};
}

function update(input) {
	threshold = input.value;
	updateCanvas();
}