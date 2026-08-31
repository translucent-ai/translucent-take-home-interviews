import { useEffect, useState } from 'react';

type Remit = {
  remit_id: string;
  claim_id: string;
  amount_billed: number;
  amount_paid: number;
  reason: string;
  department: string;
  service_date: string;
};

export default function App() {
  const [remits, setRemits] = useState<Remit[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/remits')
      .then((res) => (res.ok ? res.json() : Promise.reject(new Error(res.statusText))))
      .then(setRemits)
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <p>Failed to load the remittance feed: {error}</p>;
  if (!remits) return <p>Loading…</p>;

  return (
    <main style={{ fontFamily: 'sans-serif', margin: '2rem', maxWidth: 960 }}>
      <h1>Denials Dashboard</h1>

      <section>
        <h2>Summary</h2>
        {/* TODO: fetch your /api/summary endpoint and render it here.
            Recharts is installed. */}
        <p style={{ color: '#888' }}>Summary panel not implemented yet.</p>
      </section>

      <section>
        <h2>Remittance feed</h2>
        <table cellPadding={6} style={{ borderCollapse: 'collapse', width: '100%' }}>
          <thead>
            <tr style={{ textAlign: 'left', borderBottom: '2px solid #ccc' }}>
              <th>Claim</th>
              <th>Department</th>
              <th>Billed</th>
              <th>Paid</th>
              <th>Reason</th>
              <th>Service date</th>
            </tr>
          </thead>
          <tbody>
            {remits.map((r, i) => (
              <tr key={`${r.remit_id}-${i}`} style={{ borderBottom: '1px solid #eee' }}>
                <td>{r.claim_id}</td>
                <td>{r.department}</td>
                <td>${r.amount_billed.toLocaleString()}</td>
                <td>${r.amount_paid.toLocaleString()}</td>
                <td>{r.reason}</td>
                <td>{r.service_date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}
