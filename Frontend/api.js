import axios from "axios";

const api = axios.create({  
const API_BASE_URL = "http://127.0.0.1:8000";
});

async function searchTrainsAPI(source, destination, date) {
    const response = await fetch(
        `${API_BASE_URL}/mock-irctc/search`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                source: source,
                destination: destination,
                date: date
            })
        }
    );

    if (!response.ok) {
        throw new Error("Unable to search trains");
    }

    return await response.json();
}

async function bookTicketAPI(bookingData) {
    const response = await fetch(
        `${API_BASE_URL}/mock-irctc/book`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(bookingData)
        }
    );

    if (!response.ok) {
        throw new Error("Booking failed");
    }

    return await response.json();
}

async function predictAvailabilityAPI() {
    const response = await fetch(
        `${API_BASE_URL}/api/predict`
    );

    if (!response.ok) {
        throw new Error("Unable to get prediction");
    }

    return await response.json();
}