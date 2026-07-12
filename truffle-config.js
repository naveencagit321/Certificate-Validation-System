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
        // 🌟 Use your PRIVATE_KEY instead of a mnemonic phrase
        process.env.PRIVATE_KEY, 
        // 🌟 Use your full SEPOLIA_RPC_URL directly instead of building the string
        process.env.SEPOLIA_RPC_URL
      ),
      network_id: 11155111,         // Sepolia's standard network ID
      gas: 3000000,                 // 🌟 Lowered from 5500000 to reduce upfront 
      gasPrice: 15000000000,                // Gas limit
      confirmations: 2,             // Number of confirmations to wait between deployments
      timeoutBlocks: 200,           // Increase timeout threshold
      networkCheckTimeout: 1000000, // Amount of time to wait for a node connection (in ms)
      skipDryRun: true
    }
  },
  compilers: {
    solc: {
      version: "0.8.13",
    },
  },
};
