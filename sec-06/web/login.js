// ====================================
// Elements
// ====================================

const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");

const phoneInput = document.getElementById("phone");
const nameInput = document.getElementById("customer-name-input");

const message = document.getElementById("message");

const loginButton = document.getElementById("submit-button");
const registerButton = document.getElementById("register-button");

let pendingPhone = null;


// ====================================
// Open Chat
// ====================================

function openChat(customer) {

    // Save customer information for this demo tab
    sessionStorage.setItem(
        "demo_customer",
        JSON.stringify({
            id: customer.id,
            customer_name: customer.customer_name,
            phone: customer.phone
        })
    );

    // Navigate to Chat Screen
    window.location.href = "/chat";
}


// ====================================
// Show Message
// ====================================

function showMessage(text, color = "#94a3b8") {

    message.textContent = text;
    message.style.color = color;

}


// ====================================
// Reset registration when phone changes
// ====================================

phoneInput.addEventListener("input", () => {

    pendingPhone = null;
    registerForm.hidden = true;

    showMessage("");

});


// ====================================
// Customer Login
// ====================================

loginForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    const phone = phoneInput.value.trim();

    registerForm.hidden = true;
    pendingPhone = null;

    showMessage("Checking your phone number...");

    loginButton.disabled = true;
    phoneInput.disabled = true;

    try {

        const response = await fetch("/customers/lookup", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                phone: phone
            })

        });

        const data = await response.json();

        // Customer does not exist
        if (response.status === 404) {

            pendingPhone = phone;

            registerForm.hidden = false;

            showMessage(
                "New customer! Please enter your name.",
                "#3b82f6"
            );

            nameInput.focus();

            return;
        }

        // Invalid phone number
        if (response.status === 422) {

            throw new Error("Invalid phone number.");

        }

        // Other errors
        if (!response.ok) {

            throw new Error("Unable to check customer.");

        }

        // Existing customer
        showMessage(
            `Welcome back, ${data.customer_name}!`,
            "#22c55e"
        );

        openChat(data);

    } catch (error) {

        showMessage(error.message, "#ef4444");

    } finally {

        loginButton.disabled = false;
        phoneInput.disabled = false;

    }

});


// ====================================
// Customer Registration
// ====================================

registerForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    const customerName = nameInput.value.trim();

    if (!pendingPhone) {
        showMessage("Please check your phone number first.", "#ef4444");
        return;
    }

    if (customerName.length < 2) {
        showMessage("Please enter a valid name.", "#ef4444");
        return;
    }

    showMessage("Creating your account...");

    registerButton.disabled = true;
    loginButton.disabled = true;
    phoneInput.disabled = true;

    try {

        const response = await fetch("/customers/register", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                phone: pendingPhone,
                customer_name: customerName
            })

        });

        const data = await response.json();

        if (!response.ok) {

            throw new Error("Failed to register customer.");

        }

        showMessage(
            `Welcome, ${data.customer_name}!`,
            "#22c55e"
        );

        // New customer -> Chat
        openChat(data);

    } catch (error) {

        showMessage(error.message, "#ef4444");

    } finally {

        registerButton.disabled = false;
        loginButton.disabled = false;
        phoneInput.disabled = false;

    }

});