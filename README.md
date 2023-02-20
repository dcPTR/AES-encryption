# AES Encrypted File Transfer
Bezpieczeństwo Systemów Komputerowych


1. General description
	Communication is carried out in peer to peer architecture and is based on TCP protocol. The TCPHandler class creates 2 TCP sockets: one listening for messages and the other - sending messages. Listening for received messages by the server is done in a separate thread (the listening method is synchronous, so the main program class has control over the thread). By using timeouts, the server can be safely terminated.

2. Message structure
	Messages are divided into 4 types: acknowledgment of receipt, technical with length information, technical for public key exchange, and the actual message with message data. The message contains 3 fields: type identifier, parameter, and data. The fields have a fixed length determined in bytes.

    Detailed description of the message:
    + NUM - technical
        + parameter: number of segments of the incoming message
        + data: file name (optional)
    + ACK - acknowledgement of receipt (other fields empty)
    + MSG - message with message data
        + parameter: segment number
        + data: message data
    + PUB - message exchanging public key
        + parameter: allows to determine whether the key should be exchanged in response to the received packet
        + data: key

    Segment lengths:
    + Command - 16 bytes
    + Parameter - 64 bytes
    + Data - 64512 bytes

    The total message length is less than the limit imposed by the TCP protocol (2<sup>16</sup> = 65536 bytes)

3. Sending messages
	Messages are divided into segments (command, parameter, data) of pre-selected lengths. In addition, messages exceeding the maximum size are broken into smaller fragments and numbered.
	For this purpose, first the number of fragments needed is calculated, and then data is assigned to them in a loop.
    While the data is being sent, the progress bar of the GUI interface is updated.
    
    MessageSender
	Due to the more complex nature of operating on the actual messages intended for communication, their handling of their sending has been extracted into a separate class. It provides the send_message method, it requires a parameter with a reference to a running TCPHandler instance (in order to have access to the currently running client instance - the application is designed so that only one socket send/receive pair can work), but the rest of the operations in the private methods are independent. This separates the merging of file segments and the sending of necessary technical messages from the TCPHandler class.

4. Receiving messages
	Messages are not received directly, but are stored in a queue, which is read from the program level. In practice, the queue is checked in a separate thread in a loop listening for non-empty messages. In addition, messages exceeding the maximum size are combined from smaller, numbered fragments and only stored in the queue.
	To do this, first the indexes of consecutive fragments are loaded into a local list (the loop searches for segments with consecutive numbers, this protects against the accident when messages arrive in the wrong order). 	Then this list is iterated and, based on it, the appropriate fragments are added to the resulting message. The result thus obtained is added to the receiving queue.
	The listening thread, upon receiving the message, sends an ACK (acknowledgment of receipt) type of return message, it also starts a signal (event) to update the program's UI. The thread is also monitored by a progress bar from the UI, allowing the user to see how fast the data is being sent.

5. Receipt confirmation
	Receipt confirmation was implemented without using a signal (event). Instead, an existing thread of the main program which is responsible for listening was used. Thanks to this, in the class responsible for communication, it is enough to change the flag immediately after receiving a message of type ACK, and the listening thread will be able to capture this information with the accuracy of the established timeout (currently 5s).



<p align="center">
  <img src="https://github.com/dcPTR/AES-encryption/blob/main/screenshots/gui.png?raw=true" width=50% height=50% alt="GUI">
</p>

