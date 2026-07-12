// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Certification {
    address public owner;

    struct Certificate {
        string studentName;
        string courseName;
        string organization;
        string ipfsHash;
    }

    mapping(string => Certificate) private certificates;

    event CertificateIssued(string indexed uid, string studentName, string courseName);

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
        certificates[_uid] = Certificate(_name, _course, _org, _ipfs);
        emit CertificateIssued(_uid, _name, _course);
    }

    // Getter method returns the stored certificate data without revocation state
    function getCertificate(string memory _uid) public view returns (
        string memory, string memory, string memory, string memory
    ) {
        Certificate memory cert = certificates[_uid];
        require(bytes(cert.studentName).length > 0, "Certificate record absent.");
        return (cert.studentName, cert.courseName, cert.organization, cert.ipfsHash);
    }
}