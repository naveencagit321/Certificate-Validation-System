// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Certification {
    address public owner;

    struct Certificate {
        string studentName;
        string courseName;
        string organization;
        string ipfsHash;
        bool isRevoked; // 🌟 1. On-chain state tracking switch
    }

    mapping(string => Certificate) private certificates;

    event CertificateIssued(string indexed uid, string studentName, string courseName);
    event CertificateRevoked(string indexed uid);

    modifier onlyOwner() {
        require(msg.sender == owner, "Error: Caller is not the authorized administrator.");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    // Update issuance function to explicitly initialize the status as false (not revoked)
    function issueCertificate(
        string memory _uid, 
        string memory _name, 
        string memory _course, 
        string memory _org,
        string memory _ipfs
    ) public onlyOwner {
        require(bytes(certificates[_uid].studentName).length == 0, "Error: Certificate UID already exists.");
        certificates[_uid] = Certificate(_name, _course, _org, _ipfs, false);
        emit CertificateIssued(_uid, _name, _course);
    }

    // 🌟 2. THE REAL REVOCATION WRITER FUNCTION
    function revokeCertificate(string memory _uid) public onlyOwner {
        require(bytes(certificates[_uid].studentName).length > 0, "Error: Target certificate target does not exist.");
        require(!certificates[_uid].isRevoked, "Error: This target credential has already been revoked.");
        
        certificates[_uid].isRevoked = true; // Flips state flag permanently on the block ledger
        emit CertificateRevoked(_uid);
    }

    // Update getter method to pass the boolean flag back to Web3.py
    function getCertificate(string memory _uid) public view returns (
        string memory, string memory, string memory, string memory, bool
    ) {
        Certificate memory cert = certificates[_uid];
        require(bytes(cert.studentName).length > 0, "Certificate record absent.");
        return (cert.studentName, cert.courseName, cert.organization, cert.ipfsHash, cert.isRevoked);
    }
}