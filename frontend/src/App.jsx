import React, { useEffect, useState } from "react";
import ClinicTable from "./components/ClinicTable";

export default function App() {
  const [clinics, setClinics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/clinics_cleaned.json")
      .then(res => res.json())
      .then(data => {
        setClinics(data);
        setLoading(false);
      });
  }, []);

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h1>MyFootDr Clinics</h1>
      <p>Total Clinics Loaded: {clinics.length}</p>

      {loading ? <p>Loading...</p> : <ClinicTable data={clinics} />}
    </div>
  );
}
