$(document).ready(function() {
    doSlideshow();
});

var images = all_art;
var nextImageIndex = 0;
var currentImageIndex = -1;

console.log(images.length);
for (var index in images) {
    console.log(images[index]);
}

var all_art = all_art_objects;
var length = all_art.length
for (var index=0; index<length; index++){
    console.log(all_art[index])
}

function doSlideshow() {
    if (nextImageIndex >= images.length) {
        nextImageIndex = 0;
    }
    while (nextImageIndex == currentImageIndex) {
        nextImageIndex = Math.floor(Math.random() * images.length);
    }
    currentImageIndex = nextImageIndex;
    var nextImage = images[nextImageIndex++];
    
    
    //$("#background").removeClass('fadeIn').addClass('fadeOut');
    setTimeout(function() {
        $('#background').css('background-image', 'url("' + nextImage + '")');
        for (var index=0; index<length; index++){
            if ((all_art[index]['url']) == nextImage) {
                if (all_art[index]['title'] != null) {
                    document.getElementById("artwork_title").innerHTML=all_art[index]['title']
                }
    
                if (all_art[index]['artist'] != null) {
                    document.getElementById("artwork_artist").innerHTML=all_art[index]['artist']
                }
                //changePfp(document.getElementById("artwork_pfp"),"new_url")
                //https://stackoverflow.com/questions/7312553/change-image-source-with-javascript
            }
        }   
        //$("#background").removeClass('fadeOut').addClass('fadeIn');
        setTimeout(doSlideshow, 5000);
    }, 1000);
}

function changePfp(domImage, srcImage) {
    var img = new Image();
    img.onload = function()
    {
        domImg.src = this.src;
    };
    img.src = srcImage;
}
