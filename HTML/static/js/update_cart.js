document.querySelectorAll('.decrease').forEach(function (button) {
    button.addEventListener('click', function () {
        console.log('decrease')
        let quantity = parseInt(this.parentNode.id);
        let artwork_id = this.getAttribute('value');
        let newQuantity = quantity - 1;
        // prevent negative value
        if (newQuantity >= 0) {
            updateCart(newQuantity, artwork_id);
        }
    });
});

document.querySelectorAll('.increase').forEach(function (button) {
    button.addEventListener('click', function () {
        let quantity = parseInt(this.parentNode.id);
        let artwork_id = this.getAttribute('value');
        let newQuantity = quantity + 1;
        updateCart(newQuantity, artwork_id);

    });
});


function updateCart(quantity, artwork_id) {
    console.log(artwork_id, quantity)
    let user_url = '/updateCart';
    console.log(user_url);
    fetch(user_url, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ artwork_id: artwork_id, quantity: quantity }),
    })
        .then(response => response.json())
        .then(data => {
            location.reload();
        });

}

