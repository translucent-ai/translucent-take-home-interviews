import { ApolloProvider, ApolloClient, InMemoryCache, gql, useQuery } from '@apollo/client';
import React from 'react';
import DenialChart from './components/DenialChart';

const client = new ApolloClient({ uri: 'http://localhost:4000/', cache: new InMemoryCache() });
const DENIALS_QUERY = gql`query { denials { id department amount reason date } }`;

function Dashboard() {
  const { loading, error, data } = useQuery(DENIALS_QUERY);
  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error :(</p>;
  return (
    <>
      <h1>Denial Dashboard</h1>
      <DenialChart data={data.denials}/>
      <table>
        <thead><tr><th>ID</th><th>Dept</th><th>Amount</th><th>Reason</th><th>Date</th></tr></thead>
        <tbody>
          {data.denials.map((d:any)=>(
            <tr key={d.id}>
              <td>{d.id}</td><td>{d.department}</td><td>{d.amount}</td><td>{d.reason}</td><td>{d.date}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}

export default function App() {
  return <ApolloProvider client={client}><Dashboard /></ApolloProvider>
}
