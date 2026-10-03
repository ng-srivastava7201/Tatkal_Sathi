import { useState } from "react";
import { QueryClientProvider, useQuery } from "@tanstack/react-query";
import { queryClient } from "./queryClient";
import { searchTrainsAPI } from "./api";

/*
  Routes and dates based on the dataset rows provided.
  Date value is YYYY-MM-DD.
  Label is written clearly so there is no MM/DD confusion.
*/

const routeData = {
  "New Delhi": {
    "Mumbai": [
      "2027-07-11",
      "2027-04-09",
    ],
    "Kolkata": [
      "2027-03-21",
      "2027-08-27",
    ],
    "Pune": [
      "2027-03-20",
    ],
  },

  "Mumbai": {
    "New Delhi": [
      "2027-01-07",
      "2027-12-20",
    ],
    "Hyderabad": [
      "2027-01-30",
    ],
  },

  "Kolkata": {
    "New Delhi": [
      "2027-07-13",
      "2027-11-18",
    ],
  },

  "Chennai": {
    "Bengaluru": [
      "2027-11-17",
      "2027-09-10",
    ],
  },

  "Bengaluru": {
    "Chennai": [
      "2027-10-12",
      "2027-04-27",
    ],
  },

  "Hyderabad": {
    "Mumbai": [
      "2027-07-15",
      "2027-10-07",
    ],
  },

  "Pune": {
    "New Delhi": [
      "2027-05-31",
    ],
  },
};


function formatDate(dateString) {
  const [year, month, day] = dateString.split("-");

  const monthNames = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];

  return `${Number(day)} ${monthNames[Number(month) - 1]} ${year}`;
}


function TrainSearchDemo() {
  const [source, setSource] = useState("");
  const [destination, setDestination] = useState("");
  const [date, setDate] = useState("");
  const [searchEnabled, setSearchEnabled] = useState(false);

  const destinations = source
    ? Object.keys(routeData[source] || {})
    : [];

  const availableDates =
    source && destination
      ? routeData[source]?.[destination] || []
      : [];


  const {
    data,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["trains", source, destination, date],

    queryFn: () =>
      searchTrainsAPI({
        source,
        destination,
        date,
      }),

    enabled:
      searchEnabled &&
      source !== "" &&
      destination !== "" &&
      date !== "",
  });


  function handleSourceChange(event) {
    const value = event.target.value;

    setSource(value);
    setDestination("");
    setDate("");
    setSearchEnabled(false);
  }


  function handleDestinationChange(event) {
    const value = event.target.value;

    setDestination(value);
    setDate("");
    setSearchEnabled(false);
  }


  function handleDateChange(event) {
    setDate(event.target.value);
    setSearchEnabled(false);
  }


  function searchTrains() {
    if (!source || !destination || !date) {
      alert("Please select From Station, To Station and Journey Date.");
      return;
    }

    setSearchEnabled(true);
  }


  return (
    <div className="min-h-screen bg-gray-100 p-6">

      <div className="max-w-5xl mx-auto">

        {/* HEADER */}

        <div className="bg-white rounded-2xl shadow-lg p-8">

          <h1 className="text-3xl font-bold text-gray-800">
            Tatkal Sathi
          </h1>

          <p className="text-gray-600 mt-2">
            Tatkal Train Search
          </p>


          {/* SEARCH FORM */}

          <div className="grid md:grid-cols-3 gap-5 mt-8">

            {/* FROM */}

            <div>

              <label className="block text-sm font-semibold text-gray-700 mb-2">
                From Station
              </label>

              <select
                value={source}
                onChange={handleSourceChange}
                className="w-full border border-gray-300 rounded-lg px-4 py-3 bg-white"
              >

                <option value="">
                  Select From Station
                </option>

                {Object.keys(routeData).map((station) => (
                  <option
                    key={station}
                    value={station}
                  >
                    {station}
                  </option>
                ))}

              </select>

            </div>


            {/* TO */}

            <div>

              <label className="block text-sm font-semibold text-gray-700 mb-2">
                To Station
              </label>

              <select
                value={destination}
                onChange={handleDestinationChange}
                disabled={!source}
                className="w-full border border-gray-300 rounded-lg px-4 py-3 bg-white disabled:bg-gray-100"
              >

                <option value="">
                  {source
                    ? "Select To Station"
                    : "Select From First"}
                </option>

                {destinations.map((station) => (
                  <option
                    key={station}
                    value={station}
                  >
                    {station}
                  </option>
                ))}

              </select>

            </div>


            {/* DATE */}

            <div>

              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Journey Date
              </label>

              <select
                value={date}
                onChange={handleDateChange}
                disabled={!destination}
                className="w-full border border-gray-300 rounded-lg px-4 py-3 bg-white disabled:bg-gray-100"
              >

                <option value="">
                  {destination
                    ? "Select Journey Date"
                    : "Select Route First"}
                </option>

                {availableDates.map((availableDate) => (
                  <option
                    key={availableDate}
                    value={availableDate}
                  >
                    {formatDate(availableDate)}
                  </option>
                ))}

              </select>

            </div>

          </div>


          {/* SEARCH BUTTON */}

          <button
            onClick={searchTrains}
            className="mt-6 bg-blue-600 hover:bg-blue-700 text-white px-7 py-3 rounded-lg font-semibold"
          >
            Search Trains
          </button>


          {/* LOADING */}

          <div className="mt-8">

            {isLoading && (
              <div className="bg-blue-50 text-blue-700 p-4 rounded-lg">
                Searching available trains...
              </div>
            )}


            {/* ERROR */}

            {isError && (
              <div className="bg-red-50 text-red-700 p-4 rounded-lg">
                {error.message}
              </div>
            )}


            {/* RESULTS */}

            {data && (
              <div>

                <h2 className="text-2xl font-bold text-gray-800 mb-2">
                  Search Result
                </h2>

                <p className="text-gray-600 mb-5">
                  Trains found: {data.count}
                </p>


                {data.count === 0 && (
                  <div className="bg-yellow-50 text-yellow-800 p-4 rounded-lg">
                    No train is available for this selected route and date.
                  </div>
                )}


                <div className="space-y-4">

                  {data.trains.map((train, index) => (

                    <div
                      key={train.train_id ?? index}
                      className="border border-gray-200 rounded-xl p-6 bg-gray-50"
                    >

                      <div className="flex justify-between items-start gap-4">

                        <div>

                          <h3 className="text-xl font-bold text-gray-800">
                            {train.train_name ??
                              `Train ${train.train_id ?? index + 1}`}
                          </h3>

                          <p className="text-gray-600 mt-1">
                            {train.source ?? source}
                            {" → "}
                            {train.destination ?? destination}
                          </p>

                        </div>

                        <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-semibold">
                          Available
                        </span>

                      </div>


                      <div className="grid md:grid-cols-3 gap-4 mt-5">

                        <div>
                          <p className="text-sm text-gray-500">
                            Train ID
                          </p>

                          <p className="font-semibold">
                            {train.train_id ?? "N/A"}
                          </p>
                        </div>


                        <div>
                          <p className="text-sm text-gray-500">
                            Class
                          </p>

                          <p className="font-semibold">
                            {String(train.class ?? "N/A")}
                          </p>
                        </div>


                        <div>
                          <p className="text-sm text-gray-500">
                            Quota
                          </p>

                          <p className="font-semibold">
                            {String(train.quota ?? "N/A")}
                          </p>
                        </div>

                      </div>


                      <div className="grid md:grid-cols-2 gap-4 mt-4">

                        <div>
                          <p className="text-sm text-gray-500">
                            Seats Available
                          </p>

                          <p className="text-lg font-bold text-green-600">
                            {String(
                              train.seats_available_at_booking_time ??
                              train.seats_available ??
                              "N/A"
                            )}
                          </p>
                        </div>


                        <div>
                          <p className="text-sm text-gray-500">
                            Journey Date
                          </p>

                          <p className="font-semibold">
                            {formatDate(date)}
                          </p>
                        </div>

                      </div>


                      <button
                        className="mt-5 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg font-semibold"
                        onClick={() => {
                          localStorage.setItem(
                            "selectedTrain",
                            JSON.stringify(train)
                          );

                          localStorage.setItem(
                            "fromStation",
                            source
                          );

                          localStorage.setItem(
                            "toStation",
                            destination
                          );

                          localStorage.setItem(
                            "journeyDate",
                            date
                          );

                          window.location.href = "/booking.html";
                        }}
                      >
                        Select Train
                      </button>

                    </div>

                  ))}

                </div>

              </div>
            )}

          </div>

        </div>

      </div>

    </div>
  );
}


function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TrainSearchDemo />
    </QueryClientProvider>
  );
}


export default App;