const { ApolloServer, gql } = require('apollo-server');
const fs = require('fs');

const typeDefs = gql`
  type Denial { id: ID! department: String! amount: Float! reason: String! date: String! }
  type Query { denials: [Denial!]! }
`;
const denialsData = JSON.parse(fs.readFileSync('./data/denials.json'));
const resolvers = { Query: { denials: () => denialsData } };
new ApolloServer({ typeDefs, resolvers }).listen({ port: 4000 }).then(({ url }) => {
  console.log(`🚀  Server ready at ${url}`);
});
