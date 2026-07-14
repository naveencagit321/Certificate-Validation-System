import json
import os
from pathlib import Path
from web3 import Web3
from dotenv import load_dotenv

# Base directory setup to locate the .env file correctly
# .parent points to 'application'. .parent.parent points to the root project folder
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# 🌐 CONNECT TO LEDGER NETWORK
raw_url = os.getenv("SEPOLIA_RPC_URL")
if not raw_url:
    raise ValueError("Error: SEPOLIA_RPC_URL not found in environment variables. Check your .env file.")

sepolia_rpc_url = raw_url.strip()
w3 = Web3(Web3.HTTPProvider(sepolia_rpc_url))

def get_contract_abi():
    """Retrieves the clean smart contract ABI from the Truffle build artifacts."""
    root_dir = Path(__file__).resolve().parent.parent
    certification_json_path = root_dir / 'build' / 'contracts' / 'Certification.json'

    try:
        with open(certification_json_path, 'r') as json_file:
            certification_data = json.load(json_file)
            abi = certification_data.get('abi', [])
            if not abi:
                print(f"Warning: ABI is empty in {certification_json_path}")
            return abi
    except FileNotFoundError:
        print(f"Error: Truffle build artifact file {certification_json_path} not found. Run 'truffle compile' first.")
        return []

# Load contract configuration variables
contract_abi = get_contract_abi()
root_dir = Path(__file__).resolve().parent.parent
deployment_config_fpath = root_dir / "deployment_config.json"

try:
    with open(deployment_config_fpath, 'r') as json_file:
        address_data = json.load(json_file)
    contract_address = address_data.get('Certification')
    if not contract_address:
        raise ValueError(f"Certification address target not defined within {deployment_config_fpath}")
except FileNotFoundError:
    raise FileNotFoundError(f"Configuration profile {deployment_config_fpath} is missing from the workspace root.")

# 🔒 INTERACT WITH SMART CONTRACT WITH CHECKSUM ENFORCEMENT
# Ensures the string address is completely valid before parsing it to Web3
checksummed_address = Web3.to_checksum_address(contract_address.strip())
contract = w3.eth.contract(address=checksummed_address, abi=contract_abi)