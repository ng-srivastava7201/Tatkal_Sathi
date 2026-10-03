import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

export const searchTrains = async (source, destination, date) => {
  const response = await API.post("/mock-irctc/search", {
    source,
    destination,
    date,
  });

  return response.data;
};

export const predictAvailability = async () => {
  const response = await API.get("/api/predict");

  return response.data;
};

export const bookTicket = async (bookingData) => {
  const response = await API.post("/mock-irctc/book", bookingData);

  return response.data;
};

export default API;