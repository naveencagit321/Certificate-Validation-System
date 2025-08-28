# Certificate Validation System

A decentralized application (DApp) for issuing and verifying digital certificates on the blockchain. This system leverages the immutability of blockchain technology to create a tamper-proof and easily verifiable record of credentials, preventing forgery and simplifying the validation process.

## 📜 Description

Traditional certificates are prone to forgery and can be difficult to verify. This project solves that problem by storing a cryptographic hash of each certificate on an Ethereum-based blockchain. The front-end, built with Streamlit, provides a simple user interface for authorities to issue new certificates and for anyone to validate an existing certificate's authenticity in real-time.

## ✨ Features

-   **Decentralized:** Certificate records are stored on a blockchain, not a central server.
-   **Tamper-Proof:** The immutability of the blockchain ensures that certificate records cannot be altered.
-   **Easy Verification:** Anyone can quickly verify a certificate's authenticity through a simple web interface.
-   **Secure Issuance:** A straightforward process for authorized parties to issue new certificates.
-   **Containerized:** The entire application stack is containerized with Docker for easy setup and deployment.

## 🛠️ Tech Stack

-   **Blockchain:** Solidity, Truffle Suite
-   **Local Blockchain:** Ganache
-   **Frontend:** Streamlit (Python)
-   **Containerization:** Docker & Docker Compose

## 📁 Project Structure

├── application/      # Contains the Streamlit frontend source code
├── assets/           # Static assets (images, etc.) for the frontend
├── contracts/        # Solidity smart contracts
├── migrations/       # Truffle migration scripts for deployment
├── .dockerignore     # Specifies files to ignore in Docker builds
├── .gitignore        # Specifies files for Git to ignore
├── docker-compose.yml  # Defines and runs the multi-container application
├── Dockerfile.ganache  # Dockerfile for the local Ganache blockchain
├── Dockerfile.streamlit # Dockerfile for the Streamlit application
└── truffle-config.js   # Truffle configuration file
