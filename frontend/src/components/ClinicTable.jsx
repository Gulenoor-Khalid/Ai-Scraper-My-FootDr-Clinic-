import React, { useState } from "react";

export default function ClinicTable({ data }) {
  const [search, setSearch] = useState("");

  const filtered = data.filter(c =>
    c["Name of Clinic"].toLowerCase().includes(search.toLowerCase()) ||
    c["Address"].toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <input
        placeholder="Search clinics..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        style={{
          padding: "8px",
          marginBottom: "15px",
          width: "250px",
          fontSize: "16px"
        }}
      />

      <table width="100%" border="1" cellPadding="8">
        <thead>
          <tr>
            <th>Name</th>
            <th>Address</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Services</th>
            <th>URL</th>
          </tr>
        </thead>

        <tbody>
          {filtered.map((c, i) => (
            <tr key={i}>
              <td>{c["Name of Clinic"]}</td>
              <td>{c["Address"]}</td>
              <td>{c["Email"]}</td>
              <td>{c["Phone"]}</td>
              <td>{c["Services"]}</td>
              <td><a href={c["Clinic Page URL"]} target="_blank">Open</a></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
