# Connect4-multiplayer
Connect4 is a Python based multiplayer game. It utilizes sockets for real-time communication between clients. player can see live progress of his opponent and a central server.

I. Game Overview: 
Connect 4 is a two-player connection game where the objective is to be the first to form a horizontal, vertical, or diagonal line of four of your own discs.
Multiplayer aspect: This is a Python-based Connect 4 game that allows two players to connect to a server and play against each other in real-time.

II. Technology Used:
-> Frontend: html, css js
-> Backend: Python flask.
-> Client communicatio: sockets.

III. Features

Multiplayer Gameplay: Two players can connect and play against each other over a network.
Real-Time Interaction: Players see each other's moves as they happen.
Room Creation: Players can create a room with a specific name for others to join.
Color Assignment: The creator of the room is automatically assigned the color red; the joining player is assigned yellow.
Turn-Based System: Players take turns dropping their discs into the columns.
Win Condition: The game detects and announces when a player connects four discs in a row, column, or diagonally.
Real-time gameplay, where players can see each other's moves as they happen.
Networking: Explain that sockets are used for communication between the players and the server.
If applicable, describe the GUI (Graphical User Interface) using Pygame.

IV. How to Play
Create a room with a name, (red is assigned to the room creator) yellow joins from his device using the same name, red makes the first move by clicking on any colomn. players take turns one after the other. first to connect 4 dots in a row or column or diagonally wins.

"A multiplayer Connect 4 game developed in Python, where players connect to a central server to compete in real-time. The server uses sockets to manage game state and player interactions".
