// Toggle Product Sections
function toggleProductButtons() {
    const productSections = document.getElementById('product-sections');
    const mainContent = document.getElementById('page-content-wrapper');
    const productsLink = document.getElementById('products-link');
    const ordersSection = document.getElementById('orders-section');
    const ordersLink = document.getElementById('orders-link');

    // Hide orders section if it's visible
    if (ordersSection.style.display === 'block') {
        ordersSection.style.display = 'none';
        ordersLink.textContent = 'Orders';
    }

    // Toggle Product Section
    if (productSections.style.display === 'none' || productSections.style.display === '') {
        hideAllSections();
        productSections.style.display = 'block'; // Show Product Section
        loadProducts('cactus'); // Load only Cactus Products
        productsLink.textContent = 'Hide Products'; // Change button text
    } else {
        productSections.style.display = 'none'; // Hide Product Section
        mainContent.style.display = 'block'; // Return to main content
        productsLink.textContent = 'Products'; // Reset button text
    }
}





// Fetch and display all listed products
async function loadProducts() {
    const response = await fetch('/api/products');
    const products = await response.json();
    const container = document.getElementById('product-container');
    container.innerHTML = '';

    if (products.length === 0) {
        container.innerHTML = '<p>No products listed yet.</p>';
    } else {
        products.forEach(product => {
            const card = document.createElement('div');
            card.className = 'product-card';

            const imageId = `image-${product._id}`;
            const dotsId = `dots-${product._id}`;
            const images = product.images || ['static/images/default.jpg'];

            card.innerHTML = `
                <img id="${imageId}" src="/${images[0]}" alt="Product Image" width="150">
                <div class="dots" id="${dotsId}" style="text-align:center;margin:5px 0;"></div>

                <div class="product-info"><strong>${product.name}</strong></div>
                <p>Id: ${product.id}</p>
                <p>Price: ₹${product.price}</p>
                <p>Description: ${product.description}</p>

                <button onclick="editProduct(
                    '${product._id}',
                    '${product.id}',
                    '${encodeURIComponent(product.name)}',
                    '${product.price}',
                    '${encodeURIComponent(product.description)}',
                    '${encodeURIComponent(product.category || "")}',
                    '${encodeURIComponent(JSON.stringify(images))}'
                )">Edit</button>

                <button onclick="deleteProduct('${product._id}')">Delete</button>
            `;

            container.appendChild(card);

            // ✅ Create carousel dots
            const dotsContainer = document.getElementById(dotsId);
            images.forEach((_, index) => {
                const dot = document.createElement('span');
                dot.textContent = '●';
                dot.style.cursor = 'pointer';
                dot.style.margin = '0 4px';
                dot.style.color = index === 0 ? 'black' : 'lightgray';

                dot.addEventListener('click', () => {
                    document.getElementById(imageId).src = `/${images[index]}`;
                    // Update dot styles
                    [...dotsContainer.children].forEach(d => d.style.color = 'lightgray');
                    dot.style.color = 'black';
                });

                dotsContainer.appendChild(dot);
            });
        });
    }
}


let selectedImages = [];

document.getElementById('add-image-btn').addEventListener('click', () => {
    const imageInput = document.getElementById('image-upload');
    const file = imageInput.files[0];

    if (file && file.type.startsWith('image/')) {
        selectedImages.push(file); // add to array

        // Preview the image
        const reader = new FileReader();
        reader.onload = function (e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.classList.add('me-2', 'mb-2');
            img.style.width = '70px';
            img.style.height = '70px';
            img.style.objectFit = 'cover';
            img.style.borderRadius = '6px';
            document.getElementById('image-preview').appendChild(img);
        };
        reader.readAsDataURL(file);

        imageInput.value = ''; // Reset input so same image can be selected again
    }
});



// ✅ Add or Update a product
document.getElementById('product-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const productId = document.getElementById('product-id').value;
    const formData = new FormData();

    formData.append('category', document.getElementById('category').value);
    formData.append('id', document.getElementById('id').value);
    formData.append('name', document.getElementById('name').value);
    formData.append('price', document.getElementById('price').value);
    formData.append('description', document.getElementById('description').value);

    // Append all selected images
    selectedImages.forEach((file) => {
        formData.append('images', file);
    });

    const url = productId ? `/api/update_product/${productId}` : '/api/add_product';
    const method = productId ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            body: formData
        });

        if (response.ok) {
            alert(productId ? 'Product updated successfully!' : 'Product added successfully!');
            loadProducts();
            resetForm();
            selectedImages = []; // Reset selected images
            document.getElementById('image-preview').innerHTML = ''; // Clear preview
        } else {
            alert('Error processing product!');
        }
    } catch (error) {
        console.error(error);
        alert('Something went wrong!');
    }
});

function editProduct(_id, id, name, price, description, category, images) {
    document.getElementById('product-id').value = _id;
    document.getElementById('category').value = decodeURIComponent(category);
    document.getElementById('id').value = decodeURIComponent(id);
    document.getElementById('name').value = decodeURIComponent(name);
    document.getElementById('price').value = parseFloat(price);
    document.getElementById('description').value = decodeURIComponent(description);
    document.getElementById('submit-btn').textContent = 'Update Product';

    // Show existing images (preview)
    const previewContainer = document.getElementById('image-preview');
    previewContainer.innerHTML = ''; // Clear existing

    images.forEach((imgPath) => {
        const img = document.createElement('img');
        img.src = imgPath;
        img.style.width = '80px';
        img.style.marginRight = '5px';
        previewContainer.appendChild(img);
    });

    // Clear previous selected images from input
    document.getElementById('images').value = '';
}





// Delete product
async function deleteProduct(productId) {
    const response = await fetch(`/api/delete_product/${productId}`, {
        method: 'DELETE'
    });

    if (response.ok) {
        alert('Product deleted successfully!');
        loadProducts();
    } else {
        alert('Error deleting product!');
    }
}



// Reset the form after submission
function resetForm() {
    document.getElementById('product-id').value = '';
    document.getElementById('product-form').reset();
    document.getElementById('submit-btn').textContent = 'Add Product';
}






// Toggle Orders Section When Clicking on Orders Link
function toggleOrdersSection() {
    const ordersSection = document.getElementById('orders-section');
    const mainContent = document.getElementById('page-content-wrapper');
    const ordersLink = document.getElementById('orders-link');
    const productSections = document.getElementById('product-sections');
    const productsLink = document.getElementById('products-link');

    // Hide product section if it's visible
    if (productSections.style.display === 'block') {
        productSections.style.display = 'none';
        productsLink.textContent = 'Products';
    }

    // Toggle Orders Section
    if (ordersSection.style.display === 'none' || ordersSection.style.display === '') {
        hideAllSections();
        ordersSection.style.display = 'block'; // Show orders section
        ordersLink.textContent = 'Hide Orders'; // Change button text
    } else {
        ordersSection.style.display = 'none'; // Hide orders section
        mainContent.style.display = 'block'; // Return to main content
        ordersLink.textContent = 'Orders'; // Reset button text
    }
}

// Hide all sections (hides main content when switching sections)
function hideAllSections() {
    document.getElementById('orders-section').style.display = 'none';
    document.getElementById('product-sections').style.display = 'none';

    document.getElementById('user-container').style.display = 'none';
    document.getElementById('page-content-wrapper').style.display = 'none';


    // Reset button text when hiding sections
    document.getElementById('products-link').textContent = 'Products1';

    document.getElementById('orders-link').textContent = 'Orders';
    document.getElementById('users-link').textContent = 'Users';

}







// Toggle newOrder Visibility
function toggleOrders() {
    const container = document.getElementById('order-container');
    const oldOrderContainer = document.getElementById('old-order-container');
    const btn = document.getElementById('order-btn');

    // Check if orders are hidden or if the container is empty
    if (container.style.display === 'none' || container.innerHTML === '') {
        loadOrders().then(() => {
            container.style.display = 'flex'; // Show orders after loading
            btn.textContent = 'Hide Orders'; // Change button text to hide
        });
    } else {
        container.style.display = 'none'; // Hide orders on button click
        btn.textContent = 'View Orders'; // Change button text back to view
    }
}



function toggleOldOrders() {
    const oldOrderContainer = document.getElementById('old-order-container');
    const btn = document.getElementById('old-order-btn');

    // ✅ Check only display property to toggle
    if (oldOrderContainer.style.display === 'none' || oldOrderContainer.style.display === '') {
        oldOrderContainer.style.display = 'flex'; // Show old orders
        btn.textContent = 'Hide Old Orders'; // Change button text
    } else {
        oldOrderContainer.style.display = 'none'; // Hide old orders
        btn.textContent = 'Show Old Orders'; // Reset button text
    }
}



// Search Old Orders by Phone Number and Move Matching Orders to Top
function searchOldOrders() {
    const searchValue = document.getElementById('search-old-orders').value.trim();
    const orderCards = Array.from(document.querySelectorAll('#old-order-container .order-card'));

    let matchingCards = []; // Array to hold matching cards
    let nonMatchingCards = []; // Array to hold non-matching cards

    orderCards.forEach(card => {
        const phoneNumber = card.querySelector('.order-phone').textContent;

        // Check if the phone number contains the search value
        if (phoneNumber.includes(searchValue)) {
            matchingCards.push(card);
        } else {
            nonMatchingCards.push(card);
        }
    });

    const oldOrderContainer = document.getElementById('old-order-container');
    oldOrderContainer.innerHTML = ''; // Clear container

    if (matchingCards.length > 0) {
        // Add matching cards to the top
        matchingCards.forEach(card => oldOrderContainer.appendChild(card));

        // Add non-matching cards below
        nonMatchingCards.forEach(card => oldOrderContainer.appendChild(card));
    } else {
        alert('No matching orders found for this phone number.');

        // If no match, display all orders again
        orderCards.forEach(card => oldOrderContainer.appendChild(card));
    }
}



// Fetch and display orders, moving completed orders to old orders
async function loadOrders() {
    const response = await fetch('/api/orders');
    const orders = await response.json();
    const container = document.getElementById('order-container');
    const oldOrderContainer = document.getElementById('old-order-container');

    container.innerHTML = '';
    oldOrderContainer.innerHTML = '';

    if (orders.length === 0) {
        container.innerHTML = '<p class="text-muted">No orders found.</p>';
        return;
    }

    orders.forEach(order => {
        const orderCard = document.createElement('div');
        orderCard.className = 'col';
        orderCard.innerHTML = `
            <div class="order-card">
                <div class="order-header">Order #${order._id}</div>
                <div class="order-details">
                    <p><strong>User:</strong> ${order.user_name} </p>
                    <p class="order-phone"><strong>Phone:</strong> ${order.user_phone}</p>

                    <p><strong>Delivery Name:</strong> ${order.name}<br>
                    <strong>Delivery Phone:</strong> ${order.phno}</p>

                    <p><strong>Address:</strong> ${order.address}</p>
                    <p><strong>Payment:</strong> ${order.payment_method.toUpperCase()}</p>
                    <p><strong>Total:</strong> ₹${order.total_price}</p>
                    <p><strong>Payment_Status:</strong>${order.payment_status}</p>
                    <p><strong>Delhivery_Status:</strong>
                        <span class="${order.delhivery_status === 'Completed' ? 'text-success' : 'text-warning'}">
                            ${order.delhivery_status}
                        </span>
                    </p>
                    <p><strong>Order Date:</strong> ${formatDate(order.order_date)}</p>

                    <h6>Items:</h6>
                    <ul class="item-list">
                        ${order.items.map(item => `
                            <li>${item.id} - ${item.name} - ₹${item.price} x ${item.quantity}</li>
                        `).join('')}
                    </ul>

                    <div class="order-actions mt-2">
                        ${order.delhivery_status === 'Completed' ? '' : `
                            <button class="btn btn-success btn-sm" onclick="updateOrderStatus('${order._id}', 'Completed')">Mark as Completed</button>
                            <button class="btn btn-danger btn-sm" onclick="deleteOrder('${order._id}')">Delete</button>
                        `}
                    </div>
                </div>
            </div>
        `;

        // Move completed orders to Old Orders section
        if (order.delhivery_status === 'Completed') {
            oldOrderContainer.appendChild(orderCard);
        } else {
            container.appendChild(orderCard);
        }
    });
}




// Update order status and move completed orders to old orders
async function updateOrderStatus(orderId, delhivery_status) {
    const response = await fetch(`/api/update_order/${orderId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ delhivery_status })
    });

    if (response.ok) {
        alert('Order status updated successfully!');

        // Load orders again after updating
        loadOrders();
    } else {
        alert('Error updating order status!');
    }
}


// Delete order
async function deleteOrder(orderId) {
    const response = await fetch(`/api/delete_order/${orderId}`, {
        method: 'DELETE'
    });

    if (response.ok) {
        alert('Order deleted successfully!');
        loadOrders();
    } else {
        alert('Error deleting order!');
    }
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



// Toggle Users Visibility and Fetch Data
async function toggleUsers() {
    const userContainer = document.getElementById('user-container');
    const userList = document.getElementById('user-list');
    const btn = document.getElementById('users-link');
    const ordersSection = document.getElementById('orders-section');
    const mainContent = document.getElementById('page-content-wrapper');
    const ordersLink = document.getElementById('orders-link');
    const productSections = document.getElementById('product-sections');
    const productsLink = document.getElementById('products-link');

    // Hide product section if it's visible
    if (productSections.style.display === 'block') {
        productSections.style.display = 'none';
        productsLink.textContent = 'Products';
    }
    // Hide product section if it's visible
    if (ordersSection.style.display === 'block') {
        ordersSections.style.display = 'none';
        ordersLink.textContent = 'orders';
    }

    // ✅ Check if user section is visible
    if (userContainer.style.display === 'none' || userContainer.style.display === '') {
        hideAllSections(); // Hide all other sections
        await loadUsers(); // Load user data
        userContainer.style.display = 'block'; // Show user section
        btn.textContent = 'Hide Users'; // Change button text to hide
    } else {
        userContainer.style.display = 'none'; // Hide user section
        mainContent.style.display = 'block';
        btn.textContent = 'Users'; // Reset button text to show
    }
}



// Fetch and Display Users from the Database
async function loadUsers() {
    const userList = document.getElementById('user-list');

    try {
        const response = await fetch('/api/users'); // API endpoint to fetch users
        const users = await response.json();

        // ✅ Clear any previous data
        userList.innerHTML = '';

        if (users.length === 0) {
            userList.innerHTML = '<tr><td colspan="3" class="text-center">No users found.</td></tr>';
        } else {
            // ✅ Loop through each user and populate the table
            users.forEach(user => {
                const row = `
                    <tr>
                        <td>${user._id}</td>
                        <td>${user.fullname}</td>
                        <td>${user.phone}</td>
                    </tr>
                `;
                userList.innerHTML += row;
            });
        }
    } catch (error) {
        console.error('Error loading users:', error);
        alert('Failed to load users. Please try again later.');
    }
}


// Fetch dashboard data
async function loadDashboardData() {
    try {
        console.log('📡 Fetching dashboard data...');

        // Fetch data from API
        const response = await fetch('/api/dashboard');

        // Check if response is OK
        if (!response.ok) {
            console.error(`❌ API Error: ${response.status} - ${response.statusText}`);
            return;
        }

        // Parse JSON data
        const data = await response.json();


        // Check if data contains expected keys
        if (data.total_users !== undefined && data.total_orders !== undefined && data.total_products !== undefined) {
            console.log('📊 Dashboard data loaded successfully!');

            // Update values in the UI
            document.getElementById('total-users').textContent = data.total_users || 1;
            document.getElementById('total-orders').textContent = data.total_orders || 0;
            document.getElementById('total-products').textContent = data.total_products || 0;
            setInterval(loadDashboardData, 30000);


        } else {
            console.warn('⚠️ Unexpected response format:', data);
        }
    } catch (error) {
        console.error('❌ Error fetching dashboard data:', error);
    }
}


 // ✅ Load data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();  // Initial data load
    setInterval(loadDashboardData, 30000);  // Auto-refresh every 30 seconds
});

// Load products on page load
window.onload = loadProducts;