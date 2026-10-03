const API_BASE_URL = "";

export interface SearchRequest {
    source: string;
    destination: string;
    date: string;
}

export interface BookingRequest {
    train_id: string;
    travel_date: string;
    class_name: string;
    quota: string;
    seats_requested: number;
}

export interface Train {
    train_id?: string;
    train_name?: string;
    train_number?: string;
    source?: string;
    destination?: string;
    availability?: number;
    seats_available?: number;
    fare?: number;
    [key: string]: unknown;
}

export interface SearchResponse {
    status: string;
    count: number;
    trains: Train[];
}

export interface PredictionResponse {
    route: string;
    success_probability: number;
    predicted_seats_available: number;
}


/* =========================
   SEARCH TRAINS
========================= */

export async function searchTrainsAPI(
    data: SearchRequest
): Promise<SearchResponse> {

    /*
      HTML date input gives:
      YYYY-MM-DD

      Dataset uses:
      DD-MM-YYYY

      Example:
      2027-07-11
      becomes
      11-07-2027
    */

    const [year, month, day] = data.date.split("-");

    const formattedDate = `${day}-${month}-${year}`;

    const response = await fetch(
        `${API_BASE_URL}/mock-irctc/search`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                source: data.source,
                destination: data.destination,
                date: formattedDate
            })
        }
    );

    if (!response.ok) {
        throw new Error("Unable to search trains");
    }

    return await response.json() as SearchResponse;
}


/* =========================
   BOOK TICKET
========================= */

export async function bookTicketAPI(
    data: BookingRequest
): Promise<unknown> {

    const response = await fetch(
        `${API_BASE_URL}/mock-irctc/book`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(data)
        }
    );

    if (!response.ok) {
        throw new Error("Booking failed");
    }

    return await response.json();
}


/* =========================
   PREDICT AVAILABILITY
========================= */

export async function predictAvailabilityAPI():
    Promise<PredictionResponse> {

    const response = await fetch(
        `${API_BASE_URL}/api/predict`
    );

    if (!response.ok) {
        throw new Error("Unable to get prediction");
    }

    return await response.json() as PredictionResponse;
}