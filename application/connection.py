import json
import os
from pathlib import Path
from web3 import Web3
from dotenv import load_dotenv

# Base directory setup to locate the .env file correctly
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Connect to the live Sepolia network using your Alchemy URL from the .env file
# Connect to the live Sepolia network using your Alchemy URL from the .env file
raw_url = os.getenv("SEPOLIA_RPC_URL")
if not raw_url:
    raise ValueError("Error: SEPOLIA_RPC_URL not found in environment variables. Check your .env file.")

sepolia_rpc_url = raw_url.strip()
w3 = Web3(Web3.HTTPProvider(sepolia_rpc_url))

def get_contract_abi():
    # .parent points to 'application'. .parent.parent points to the root 'Certificate Validation System' folder
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
        print(f"Error: {certification_json_path} not found.")
        return []

contract_abi = get_contract_abi()
root_dir = Path(__file__).resolve().parent.parent
deployment_config_fpath = root_dir / "deployment_config.json"

with open(deployment_config_fpath, 'r') as json_file:
    address_data = json.load(json_file)
contract_address = address_data.get('Certification')

# Interact with the live smart contract
contract = w3.eth.contract(address=contract_address, abi=contract_abi)