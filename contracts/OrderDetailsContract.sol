// SPDX-License-Identifier: MIT
pragma solidity 0.8.0;

contract TransactionRecorder {
    // Define a structure to hold transaction details
    struct Transaction {
        uint256 id;
        address from;
        address to;
        uint256 amount;
        string details;
    }

    // State variable to keep track of transactions
    Transaction[] public transactions;

    // Event to emit when a transaction is recorded
    event TransactionRecorded(uint256 indexed id, address indexed from, address indexed to, uint256 amount, string details);

    // Function to record a transaction
    function recordTransaction(address _to, uint256 _amount, string memory _details) public {
        uint256 transactionId = transactions.length;
        transactions.push(Transaction(transactionId, msg.sender, _to, _amount, _details));

        emit TransactionRecorded(transactionId, msg.sender, _to, _amount, _details);
    }

    // Function to retrieve a specific transaction's details
    function getTransaction(uint256 _id) public view returns (Transaction memory) {
        require(_id < transactions.length, "Transaction does not exist.");
        return transactions[_id];
    }

    // Function to get the total number of transactions
    function getTotalTransactions() public view returns (uint256) {
        return transactions.length;
    }
}
