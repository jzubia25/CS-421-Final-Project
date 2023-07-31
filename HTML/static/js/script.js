//Using built in FileReader API, to create a file preview on the client-side before uploading
let imagePreview = document.querySelector(".image-preview");
let newImg = document.createElement("img");
newImg.setAttribute("style", "max-width: 100%; max-height: 100%;");

document
  .querySelector(".fileInput")
  .addEventListener("change", function (e) {
    console.log(e);
    let file = e.target.files[0];
    if (file) {
      let reader = new FileReader();
      reader.onload = function (e) {
        console.log(e);
        newImg.setAttribute("src", e.target.result);
        imagePreview.appendChild(newImg);
      };
      reader.readAsDataURL(file);
    }
  });