require('dotenv').config();
const HDWalletProvider = require('@truffle/hdwallet-provider');
module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",
      port: 8545,
      network_id: "*",
    },
    sepolia: {
      provider: () => new HDWalletProvider(
        process.env.PRIVATE_KEY, 
        process.env.SEPOLIA_RPC_URL
      ),
      network_id: 11155111, // Sepolia's official network ID
      gas: 5500000,         // Gas limit
      confirmations: 2,     // Wait for 2 confirmations to ensure deployment
      timeoutBlocks: 200,   // Wait time before failing
      skipDryRun: true      // Skip dry run before migrations
    }
  },
  compilers: {
    solc: {
      version: "0.8.13",
    },
  },
};