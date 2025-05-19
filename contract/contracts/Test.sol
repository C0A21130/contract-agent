// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.28;

// Uncomment this line to use console.log
// import "hardhat/console.sol";

contract Test {
    mapping(address => string) public names;

    function setName(string memory name) public {
        names[msg.sender] = name;
    }

    function getName() public view returns (string memory) {
        return names[msg.sender];
    }
}
