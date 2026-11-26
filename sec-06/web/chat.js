// ========================================
// 1. Current Customer
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

const customerName =
    document.getElementById("customer-name");

const chatMessages =
    document.getElementById("chat-messages");

const chatForm =
    document.getElementById("chat-form");

const messageInput =
    document.getElementById("message-input");

const sendButton =
    document.getElementById("send-button");

const chatStatus =
    document.getElementById("chat-status");

const logoutButton =
    document.getElementById("logout-button");

const newChatButton =
    document.getElementById("new-chat-button");

const conversationList =
    document.getElementById("conversation-list");


// ========================================
// 3. Application State
// ========================================

let activeConversationId = null;

let conversations = [];

let isBusy = false;


// ========================================
// 4. API Helper
// ========================================

async function apiRequest(endpoint, body, failureMessage) {

    let response;

    try {

        response = await fetch(endpoint, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(body)

        });

    } catch {

        throw new Error(failureMessage);

    }

    const data = await response.json().catch(() => null);

    if (!response.ok) {

        throw new Error(
            typeof data?.detail === "string"
                ? data.detail
                : failureMessage
        );

    }

    if (data === null) {
        throw new Error(failureMessage);
    }

    return data;
}

// ========================================
// 5. UI Helpers
// ========================================

function showStatus(text, isError = false) {

    chatStatus.textContent = text;

    chatStatus.style.color = isError
        ? "#ef4444"
        : "#94a3b8";
}


function setBusy(value) {

    isBusy = value;

    newChatButton.disabled = value;

    messageInput.disabled =
        value || !activeConversationId;

    sendButton.disabled =
        value || !activeConversationId;

    conversationList
        .querySelectorAll("button")
        .forEach(button => {

            button.disabled = value;

        });
}


function clearMessages() {

    chatMessages.replaceChildren();

}


function addMessage(text, role) {

    const messageDiv =
        document.createElement("div");

    messageDiv.classList.add("message");

    messageDiv.classList.add(
        role === "user"
            ? "user-message"
            : "assistant-message"
    );

    const paragraph =
        document.createElement("p");

    paragraph.textContent = text;

    messageDiv.appendChild(paragraph);

    chatMessages.appendChild(messageDiv);

    chatMessages.scrollTop =
        chatMessages.scrollHeight;
}


function showWelcomeMessage() {

    clearMessages();

    addMessage(
        `Hello ${customer.customer_name}! ` +
        "How can I help you today?",
        "assistant"
    );

}

// ========================================
// 6. Load Conversations
// ========================================

async function loadConversations() {

    conversations = await apiRequest(
        "/conversations/list",
        {
            phone: customer.phone
        },
        "Couldn't load your conversations. Reload the page to try again."
    );

    renderConversations();
}

// ========================================
// 7. Render Conversations
// ========================================

function renderConversations() {

    conversationList.replaceChildren();

    if (conversations.length === 0) {

        const paragraph =
            document.createElement("p");

        paragraph.className =
            "sidebar-placeholder";

        paragraph.textContent =
            "No conversations yet.";

        conversationList.appendChild(paragraph);

        return;
    }

    conversations.forEach(conversation => {

        const button =
            document.createElement("button");

        button.type = "button";

        button.className = "conversation-item";

        button.disabled = isBusy;

        const date = new Date(
            conversation.created_at
        );

        button.textContent =
            "Chat — " + date.toLocaleString();

        if (
            conversation.id === activeConversationId
        ) {
            button.classList.add("active");
            button.setAttribute("aria-current", "true");
        }

        button.addEventListener("click", () => {

            openConversation(conversation.id);

        });

        conversationList.appendChild(button);

    });

}

// ========================================
// 8. Open Conversation
// ========================================

async function openConversation(conversationId) {

    if (isBusy) {
        return;
    }

    setBusy(true);

    showStatus("Loading conversation...");

    try {

        const history = await apiRequest(
            "/conversations/history",
            {
                phone: customer.phone,
                conversation_id: conversationId
            },
            "Couldn't load this conversation. Select it to try again."
        );

        activeConversationId = conversationId;

        clearMessages();

        if (history.length === 0) {

            showWelcomeMessage();

        } else {

            history.forEach(message => {

                addMessage(
                    message.content,
                    message.role
                );

            });

        }

        renderConversations();

        messageInput.placeholder =
            "Ask me about your tickets...";

        showStatus("Conversation loaded.");

    } catch (error) {

        showStatus(error.message, true);

    } finally {

        setBusy(false);

    }

}


// ========================================
// 9. Initialize Application
// ========================================

async function initializeChat() {

    if (!customer || !customer.id || !customer.phone) {

        window.location.replace("/login");

        return;
    }

    customerName.textContent =
        customer.customer_name;

    showWelcomeMessage();

    setBusy(true);

    try {

        await loadConversations();

    } catch (error) {

        conversationList.textContent = "Conversations unavailable.";
        showStatus(error.message, true);
        return;

    } finally {

        setBusy(false);

    }

    if (conversations.length > 0) {
        await openConversation(
            conversations[0].id
        );
    } else {

        showStatus(
            "Click New Chat to start a conversation."
        );

    }

}


chatForm.addEventListener("submit", async event => {

    event.preventDefault();

    const message = messageInput.value.trim();

    if (
        !message ||
        !activeConversationId ||
        isBusy
    ) {
        return;
    }

    await sendMessage(message);

});


logoutButton.addEventListener("click", () => {

    sessionStorage.removeItem("demo_customer");

    window.location.replace("/login");

});

// ========================================
// Create New Conversation
// ========================================

async function createConversation() {

    if (isBusy) {
        return;
    }

    setBusy(true);

    showStatus("Creating conversation...");

    try {

        const conversation = await apiRequest(
            "/conversations",
            {
                phone: customer.phone
            },
            "Couldn't confirm the new conversation. Reload the page to check the list."
        );

        activeConversationId =
            conversation.conversation_id;

        showWelcomeMessage();

        messageInput.value = "";

        messageInput.placeholder =
            "Ask me about your tickets...";

        conversations.unshift({
            id: conversation.conversation_id,
            created_at: conversation.created_at
        });
        renderConversations();

        showStatus("New conversation created.");

    } catch (error) {

        showStatus(error.message, true);

    } finally {

        setBusy(false);

        messageInput.focus();

    }

}


newChatButton.addEventListener("click", () => {

    createConversation();

});

// ========================================
// Send Message
// ========================================

async function sendMessage(message) {

    if (isBusy || !activeConversationId) {
        return;
    }

    setBusy(true);

    showStatus("AI is thinking...");

    const conversationId = activeConversationId;
    const unconfirmedMessage =
        "Couldn't confirm your message was saved. " +
        "Reopen this conversation to check before sending again.";

    try {

        const result = await apiRequest(
            "/conversations/message",
            {
                phone: customer.phone,

                conversation_id: conversationId,

                message: message
            },
            unconfirmedMessage
        );

        if (
            result.conversation_id !== conversationId ||
            typeof result.answer !== "string" ||
            !result.answer.trim()
        ) {
            throw new Error(unconfirmedMessage);
        }

        // The API only returns a valid answer after saving the pair.
        addMessage(message, "user");
        addMessage(result.answer, "assistant");
        messageInput.value = "";

        showStatus("AI Assistant is ready.");

    } catch (error) {

        showStatus(
            `${error.message} Your draft is still in the message box.`,
            true
        );

    } finally {

        setBusy(false);

        messageInput.focus();

    }

}

initializeChat();
