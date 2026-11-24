// ========================================
// 1. Get Current Customer
// ========================================

let customer = null;

try {
    customer = JSON.parse(
        sessionStorage.getItem("demo_customer")
    );
} catch (error) {
    customer = null;
}


// ========================================
// 2. UI Elements
// ========================================

const customerName = document.getElementById("customer-name");
const welcomeMessage = document.getElementById("welcome-message");

const chatMessages = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");

const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");

const chatStatus = document.getElementById("chat-status");
const logoutButton = document.getElementById("logout-button");


// ========================================
// 3. Chat Session
// ========================================

let sessionId = null;


// ========================================
// 4. Display a Message
// ========================================

function addMessage(text, role) {

    const messageDiv = document.createElement("div");

    messageDiv.classList.add("message");

    if (role === "user") {
        messageDiv.classList.add("user-message");
    } else {
        messageDiv.classList.add("assistant-message");
    }

    const paragraph = document.createElement("p");

    // Display text safely, without interpreting HTML
    paragraph.textContent = text;

    messageDiv.appendChild(paragraph);

    chatMessages.appendChild(messageDiv);

    // Automatically scroll to the latest message
    chatMessages.scrollTop = chatMessages.scrollHeight;
}


// ========================================
// 5. Start Chat Session
// ========================================

async function startChatSession() {

    chatStatus.textContent = "Connecting to AI Assistant...";

    try {

        const response = await fetch("/chat/sessions", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                phone: customer.phone
            })

        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                typeof data.detail === "string"
                    ? data.detail
                    : "Failed to start chat session."
            );
        }

        // Save session ID
        sessionId = data.session_id;

        // Enable chat
        messageInput.disabled = false;
        sendButton.disabled = false;

        messageInput.placeholder = "Ask me about your tickets...";

        chatStatus.textContent = "AI Assistant is ready.";

        messageInput.focus();

    } catch (error) {

        chatStatus.textContent = error.message;
        chatStatus.style.color = "#ef4444";

    }

}


// ========================================
// 6. Send Message
// ========================================

async function sendMessage(message) {

    // Prevent sending without an active session
    if (!sessionId) {
        return;
    }

    // Display user message
    addMessage(message, "user");

    // Disable input while waiting
    messageInput.disabled = true;
    sendButton.disabled = true;

    chatStatus.textContent = "AI is thinking...";

    try {

        const response = await fetch("/chat/message", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                session_id: sessionId,
                message: message
            })

        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                typeof data.detail === "string"
                    ? data.detail
                    : "Failed to get AI response."
            );
        }

        // Display AI response
        addMessage(data.answer, "assistant");

        chatStatus.textContent = "AI Assistant is ready.";
        chatStatus.style.color = "#94a3b8";

    } catch (error) {

        chatStatus.textContent = error.message;
        chatStatus.style.color = "#ef4444";

    } finally {

        messageInput.disabled = false;
        sendButton.disabled = false;

        messageInput.focus();

    }

}


// ========================================
// 7. Handle Form Submission
// ========================================

chatForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    const message = messageInput.value.trim();

    if (!message || !sessionId) {
        return;
    }

    // Clear input
    messageInput.value = "";

    await sendMessage(message);

});


// ========================================
// 8. Logout
// ========================================

logoutButton.addEventListener("click", () => {

    sessionStorage.removeItem("demo_customer");

    window.location.replace("/login");

});


// ========================================
// 9. Initialize Chat
// ========================================

if (!customer || !customer.id || !customer.phone) {

    window.location.replace("/login");

} else {

    customerName.textContent = customer.customer_name;

    welcomeMessage.textContent =
        `Hello ${customer.customer_name}! ` +
        "I'm your AI Ticket Assistant. " +
        "How can I help you today?";

    startChatSession();

}