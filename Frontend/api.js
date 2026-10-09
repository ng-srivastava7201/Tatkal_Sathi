const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function loginAPI(username, password) {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || data.message || "Login failed");
    }
    return data;
}

async function signupAPI(userData) {
    const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(userData)
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || data.message || "Sign up failed");
    }
    return data;
}

async function getRegisteredUsersAPI() {
    const response = await fetch(`${API_BASE_URL}/api/auth/users`);
    return await response.json();
}

async function searchTrainsAPI(source, destination, date, class_name = "3A", quota = "Tatkal") {
    const response = await fetch(`${API_BASE_URL}/mock-irctc/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            source: source,
            destination: destination,
            date: date,
            class_name: class_name,
            quota: quota
        })
    });

    if (!response.ok) {
        throw new Error("Unable to search trains");
    }

    return await response.json();
}

async function getSupportedStationsAPI() {
    const response = await fetch(`${API_BASE_URL}/mock-irctc/stations`);
    return await response.json();
}

async function bookTicketAPI(bookingData) {
    const response = await fetch(`${API_BASE_URL}/mock-irctc/book`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(bookingData)
    });

    if (!response.ok) {
        throw new Error("Booking failed");
    }

    return await response.json();
}

async function getAutomationStatusAPI() {
    const response = await fetch(`${API_BASE_URL}/api/automation/status`);
    return await response.json();
}

async function triggerAutomationSimulationAPI(bookingDetails = {}) {
    const response = await fetch(`${API_BASE_URL}/api/automation/trigger`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(bookingDetails)
    });
    return await response.json();
}

async function updateAutomationScheduleAPI(hour = 10, minute = 0) {
    const response = await fetch(`${API_BASE_URL}/api/automation/schedule`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ hour, minute })
    });
    return await response.json();
}

async function getAutomationHistoryAPI() {
    const response = await fetch(`${API_BASE_URL}/api/automation/history`);
    return await response.json();
}
async function predictAvailabilityAPI(routeData) {
    const response = await fetch(`${API_BASE_URL}/api/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(routeData)
    });

    if (!response.ok) {
        throw new Error("Unable to get prediction");
    }

    return await response.json();
}