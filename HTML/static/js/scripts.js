$(document).ready(function() {
    doSlideshow();
});

var slideshowImages = all_art //these are urls

var images = all_art;

var nextImageIndex = 0;
var currentImageIndex = -1;

console.log(slideshowImages.length);
// for (var index in images) {
//     console.log(images[index]);
// }

var all_artwork_info = all_art_objects; //art objects currently in database
var all_users = all_user_objects;

console.log("number of users", all_users.length);

var numSlideshowImages = slideshowImages.length

for (var index=0; index<numSlideshowImages; index++){
    console.log(all_art[index])
}

function doSlideshow() {
    if (nextImageIndex >= numSlideshowImages) {
        nextImageIndex = 0;
    }
    while (nextImageIndex == currentImageIndex) {
        nextImageIndex = Math.floor(Math.random() * numSlideshowImages);
    }
    currentImageIndex = nextImageIndex;
    var nextImage = images[nextImageIndex++];
    
    
    //$("#background").removeClass('fadeIn').addClass('fadeOut');
    setTimeout(function() {
        $('#background').css('background-image', 'url("' + nextImage + '")');
        for (var index=0; index<numSlideshowImages; index++){
            if ((all_artwork_info[index]['url']) == nextImage) {
                if (all_artwork_info[index]['title'] != null) {
                    document.getElementById("artwork_title").innerHTML=all_artwork_info[index]['title']
                } else {
                    document.getElementById("artwork_title").innerHTML="Untitled"
                }
    
                if (all_artwork_info[index]['artist'] != null) {
                    document.getElementById("artwork_artist").innerHTML=all_artwork_info[index]['artist']

                    var artist = all_artwork_info[index]['artist']
                    console.log(artist)
                    
                    for (var newIndex=0; newIndex<all_users.length; newIndex++) {
                        if ((all_users[newIndex]['profilePhotoLink'] != null) && (artist == all_users[newIndex]['userName'])) {
                            document.getElementById("artwork_pfp").src = all_users[newIndex]['profilePhotoLink']
                        }

                        if (all_users[newIndex]['profilePhotoLink'] == null) {
                            document.getElementById("artwork_pfp").src="{{ url_for('static', filename='img/ArtVision_Logo.svg')}}"
                        }
                    }
                } else {
                    document.getElementById("artwork_artist").innerHTML="ArtVision Member"
                    document.getElementById("artwork_pfp").src ="{{url_for('static', filename='img/ArtVision_Logo.svg')}}"
                }
            }
        }   
        //$("#background").removeClass('fadeOut').addClass('fadeIn');
        setTimeout(doSlideshow, 5000);
    }, 1000);
}
