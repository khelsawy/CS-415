// ====================================
// Get Current Customer
// ====================================

let customer = null;

try {
    customer = JSON.parse(
        sessionStorage.getItem("demo_customer")
    );
} catch (error) {
    customer = null;
}

const form = document.getElementById("ticket-form");

const phoneInput = document.getElementById("phone");
const problemInput = document.getElementById("problem");
const urgentInput = document.getElementById("urgent");

const submitButton = document.getElementById("submit-ticket");
const statusMessage = document.getElementById("ticket-status");

const ticketResult = document.getElementById("ticket-result");


// ====================================
// Check Customer
// ====================================

if (!customer || !customer.id || !customer.phone) {

    window.location.replace("/login");

} else {

    // Fill the phone automatically
    phoneInput.value = customer.phone;

    // ====================================
    // Submit Ticket
    // ====================================

    form.addEventListener("submit", async (event) => {

        event.preventDefault();

        const message = problemInput.value.trim();

        if (message.length < 5) {
            statusMessage.textContent =
                "Please describe your problem in more detail.";
            return;
        }

        submitButton.disabled = true;

        statusMessage.textContent =
            "Our AI is classifying your ticket...";

        statusMessage.style.color = "#94a3b8";

        ticketResult.hidden = true;

        try {

            const response = await fetch("/customers/tickets", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    phone: customer.phone,
                    message: message,
                    urgent: urgentInput.checked
                })

            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    typeof data.detail === "string"
                        ? data.detail
                        : "Failed to create ticket."
                );
            }

            // ====================================
            // Show Created Ticket
            // ====================================

            document.getElementById("ticket-id").textContent =
                data.id;

            document.getElementById("ticket-category").textContent =
                data.category;

            document.getElementById("ticket-priority").textContent =
                data.priority;

            document.getElementById("ticket-current-status").textContent =
                data.status;

            ticketResult.hidden = false;

            statusMessage.textContent =
                "Your support ticket has been submitted!";

            statusMessage.style.color = "#22c55e";

            // Clear the form for another ticket
            problemInput.value = "";
            urgentInput.checked = false;

        } catch (error) {

            statusMessage.textContent = error.message;
            statusMessage.style.color = "#ef4444";

        } finally {

            submitButton.disabled = false;

        }

    });

}