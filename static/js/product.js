// Toggle Cart Modal visibility and refresh cart data
function toggleCart() {
    const cartModal = document.getElementById('cart-modal');
    cartModal.style.display = (cartModal.style.display === 'none') ? 'block' : 'none';

    // If the cart modal is being opened, refresh the cart
    if (cartModal.style.display === 'block') {
        refreshCart();
    }
}

// Refresh the cart data by fetching from the server
function refreshCart() {

    // Fetch the updated cart data from the server
    fetch(`/get_cart`)
        .then(response => response.json())
        .then(data => {
            const cartList = document.getElementById('cart-list');
            cartList.innerHTML = '';  // Clear existing cart


            let totalPrice = 0;  // Variable to calculate total price

            if (data.cart.length > 0) {
                let ul = document.createElement('ul');
                data.cart.forEach(item => {
                    let li = document.createElement('li');
                    const totalItemPrice = (item.price * item.quantity).toFixed(2);  // Calculate total price

                    // ✅ Create Cart Item Container
                    li.innerHTML = `
                        <div class="cart-item">
                            <!-- Product Image -->


                            <img src="/${item.image}" alt="${item.name}" class="cart-item-img"/>

                            <div class="cart-item-details">

                                <p><strong>${item.name}</strong></p>
                                <p>${item.id}</p>
                                <p>Quantity: ${item.quantity}</p>
                                <p>Total Price: $${totalItemPrice}</p>
                            </div>
                        </div>
                    `;

                        // ✅ Create a container for the buttons
                        const buttonContainer = document.createElement('div');
                        buttonContainer.className = 'cart-buttons';  // Add a class for styling
                    // ✅ Add Reduce Button
                    const reduceButton = document.createElement('button');
                    reduceButton.textContent = 'Reduce';
                    reduceButton.onclick = () => reduceItem(item.productId);
                    buttonContainer.appendChild(reduceButton);

                    // ✅ Add Add Button
                    const addButton = document.createElement('button');
                    addButton.textContent = 'Add';
                    addButton.onclick = () => addItem(item.productId);
                    buttonContainer.appendChild(addButton);

                    // ✅ Add Remove Button
                    const removeButton = document.createElement('button');
                    removeButton.textContent = 'Remove';
                    removeButton.onclick = () => removeItem(item.productId);
                    buttonContainer.appendChild(removeButton);

                    // ✅ Append button container to list item
                    li.appendChild(buttonContainer);

                    ul.appendChild(li);
                    totalPrice += parseFloat(totalItemPrice); // Add item price to total price
                });
                cartList.appendChild(ul);

                // ✅ Display the total price
                const totalElement = document.createElement('p');
                totalElement.textContent = `Total Price: $${totalPrice.toFixed(2)}`;
                cartList.appendChild(totalElement);
            } else {
                cartList.innerHTML = '<p>Your cart is empty!</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching cart:', error);
            alert('An error occurred while refreshing the cart.');
        });
}


        // Reduce item quantity in the cart
        function reduceItem(productId) {
            const data = {
                productId: productId

            };

            fetch('/reduce_from_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {

                    refreshCart();
                } else {
                    alert('Failed to reduce product: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while reducing the product quantity.');
            });
        }

        // Add item quantity in the cart
        function addItem(productId) {
            const data = {
                productId: productId

            };

            fetch('/add_to_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {

                    refreshCart();
                      // 👈 Trigger shake on add

                } else {
                    alert('Failed to add product: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while adding the product quantity.');
            });
        }

function triggerCartShake() {
    const cartIcon = document.getElementById('cart-button');
    cartIcon.classList.add('shake');

    setTimeout(() => {
        cartIcon.classList.remove('shake');
    }, 500); // matches the duration of the animation
}



        // Remove item from the cart
        function removeItem(productId) {
            const data = {
                productId: productId

            };

            fetch('/remove_from_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {

                    refreshCart();  // Refresh the cart after removing the item
                    triggerCartShake();  // 👈 Trigger shake on remove
                } else {
                    alert('Failed to remove product: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while removing the product.');
            });
        }


        // Toggle About Modal visibility and fetch user details
function toggleAbout() {
    const aboutModal = document.getElementById('about-modal');
    aboutModal.style.display = (aboutModal.style.display === 'none') ? 'block' : 'none';

    // If modal is being opened, fetch user details
    if (aboutModal.style.display === 'block') {
        fetchUserDetails();
    }
}

// Fetch user details from the server
function fetchUserDetails() {
    const phone = '{{ phone }}';  // Get phone from session

    fetch(`/get_user_details`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const userDetails = `
                    <p><strong>Full Name:</strong> ${data.user.fullname}</p>
                    <p><strong>Phone:</strong> ${data.user.phone}</p>
                `;
                document.getElementById('user-details').innerHTML = userDetails;
            } else {
                document.getElementById('user-details').innerHTML = '<p>Error fetching user details!</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching user details:', error);
            document.getElementById('user-details').innerHTML = '<p>An error occurred while fetching user details.</p>';
        });
}

// Toggle Orders Modal visibility and fetch order history
function toggleOrders() {
    const ordersModal = document.getElementById('orders-modal');
    ordersModal.style.display = (ordersModal.style.display === 'none') ? 'block' : 'none';

    // If modal is being opened, fetch order history
    if (ordersModal.style.display === 'block') {
        fetchOrderHistory();
    }
}

function fetchOrderHistory() {
    fetch(`/get_order_history`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let orderList = '<ul>';
                data.orders.forEach(order => {
                    console.log('Raw Order Date:', order.order_date); // Debug Date

                  orderList += `
                        <div class="order-item">
                            <div class="order-header">
                                <strong>Order Date:</strong> ${formatDate(order.order_date)}<br>
                                <strong>Delhivery_status:</strong> ${order.delhivery_status}<br>
                                <strong>Payment_status:</strong> ${order.payment_status}<br>
                                <strong>Total Price:</strong> $${order.total_price.toFixed(2)}<br>
                            </div>

                            <div class="order-items-container">
                                ${order.items.map(item => `
                                    <div class="order-item-details">
                                        <img src="${item.image}"
                                            alt="${item.name}" class="product-image">
                                        <div class="item-info">
                                            <strong>${item.name}</strong><br>
                                            Id:${item.id}<br>
                                            Quantity: ${item.quantity}<br>
                                            Price: $${item.price.toFixed(2)}
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                });
                orderList += '</div>';
                document.getElementById('orders-list').innerHTML = orderList;
            } else {
                document.getElementById('orders-list').innerHTML = '<p>No order history found!</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching order history:', error);
            document.getElementById('orders-list').innerHTML = '<p>An error occurred while fetching order history.</p>';
        });
}



function formatDate(dateString) {
    if (!dateString) return 'N/A';

    // Check if it's in BSON format
    if (typeof dateString === 'object' && dateString.$date) {
        dateString = dateString.$date;  // Extract the ISO date string
    }

    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
        return 'Invalid Date';  // Return Invalid Date if parsing fails
    }

    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}



// Dynamically fetch cart count every second
setInterval(() => {
    fetch('/cart_count')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateCartCount(data.cartItemCount);
            }
        })
        .catch(error => console.error('Cart count fetch error:', error));
}, 1000);  // 🔁 every 1000ms

function updateCartCount(count) {
    const badge = document.getElementById('cart-count');
    if (badge) {
        badge.innerText = count;
        badge.style.display = count > 0 ? 'inline-block' : 'none';
    }
}



function updateCartButtons() {
    fetch('/get_cart')
        .then(response => response.json())
        .then(data => {
            if (data.cart && Array.isArray(data.cart)) {
                const cartItems = data.cart;
                const cartProductIds = cartItems.map(item => item.productId);

                document.querySelectorAll('button[data-product-id]').forEach(button => {
                    const pid = button.getAttribute('data-product-id');
                    if (cartProductIds.includes(pid)) {
                        button.innerText = "Added";
                        button.disabled = true;
                        button.classList.add("added");
                    } else {
                        button.innerText = "Add Product";
                        button.disabled = false;
                        button.classList.remove("added");
                    }
                });
            }
        })
        .catch(err => console.error("Error fetching cart:", err));
}

// Call every 1 second
setInterval(updateCartButtons, 1000);

