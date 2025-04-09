// Function to add product to cart
function addToCart(productId) {
    // Define the quantity as 1 for simplicity (can be modified as needed)
    let quantity = 1;

    // Create the data to send to the server
    const data = {
        productId: productId,
        quantity: quantity
    };

    // Send POST request to the server
    fetch('/add_to_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())  // Parse the response as JSON
    .then(data => {
        // Check if the product was successfully added to the cart
        if (data.success) {

            refreshCart();  // Optional: refresh cart after adding
            triggerCartShake();  // 👈 Trigger shake on add

        } else {
            alert('Failed to add product: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while adding the product to the cart.');
    });
}

function triggerCartShake() {
    const cartIcon = document.getElementById('cart-button');
    cartIcon.classList.add('shake');

    setTimeout(() => {
        cartIcon.classList.remove('shake');
    }, 500); // matches the duration of the animation
}
