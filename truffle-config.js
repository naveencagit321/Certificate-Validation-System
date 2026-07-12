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
      network_id: 11155111,
      gas: 2500000,                 // 🌟 Safely lowered down to 2.5M to drop the upfront requirement
      gasPrice: 10000000000,        // 🌟 Set to 10 gwei (standard Sepolia base price)
      confirmations: 2,
      timeoutBlocks: 200,
      networkCheckTimeout: 1000000,
      skipDryRun: true
    }
  },
  compilers: {
    solc: {
      version: "0.8.13",
    },
  },
};
