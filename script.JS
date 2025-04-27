// Handle login
document.getElementById('login-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const userId = document.getElementById('user-id').value;
    const password = document.getElementById('password').value;

    fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ id: userId, password: password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.role === 'customer') {
                document.getElementById('login-page').style.display = 'none';
                document.getElementById('customer-dashboard').style.display = 'block';
                document.getElementById('customer-name').innerText = userId;
                loadCancellationHistory();
            } else if (data.role === 'admin') {
                document.getElementById('login-page').style.display = 'none';
                document.getElementById('admin-dashboard').style.display = 'block';
                loadMealSummary();
                loadCustomerList();
            }
        } else {
            alert('Login failed. Please check your credentials.');
        }
    });
});

// Handle meal cancellation
document.getElementById('cancel-meal-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const date = document.getElementById('cancel-date').value;
    fetch('/cancel_meal', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ date: date })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Meal cancelled successfully!');
            loadCancellationHistory();
        } else {
            alert(data.message);
        }
    });
});

// Load cancellation history
function loadCancellationHistory() {
    fetch('/cancellation_history')
    .then(response => response.json())
    .then(data => {
        const history = document.getElementById('cancellation-history');
        history.innerHTML = '';
        data.history.forEach(date => {
            const li = document.createElement('li');
            li.innerText = date;
            history.appendChild(li);
        });
    });
}

// Load meal summary (admin)
function loadMealSummary() {
    fetch('/meal_summary')
    .then(response => response.json())
    .then(data => {
        document.getElementById('meal-summary').innerText = `Meals to prepare today: ${data.count}`;
    });
}

// Load customer list (admin)
function loadCustomerList() {
    fetch('/customer_list')
    .then(response => response.json())
    .then(data => {
        const list = document.getElementById('customer-list');
        list.innerHTML = '';
        data.customers.forEach(customer => {
            const li = document.createElement('li');
            li.innerHTML = `${customer.id} <button onclick="deleteCustomer('${customer.id}')">Delete</button>`;
            list.appendChild(li);
        });
    });
}

// Delete customer (admin)
function deleteCustomer(customerId) {
    fetch('/delete_customer', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ id: customerId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Customer deleted.');
            loadCustomerList();
        } else {
            alert('Failed to delete customer.');
        }
    });
}

// Logout
function logout() {
    fetch('/logout')
    .then(() => {
        window.location.reload();
    });
}

// Download PDF (admin)
function downloadPDF() {
    window.location.href = '/download_pdf';
}
