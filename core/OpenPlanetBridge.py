"""

    Handler for the communication with the in-game data aka Openplanet

"""

import socket
import json
import threading
import config


class OpenPlanetBridge:
    """
        Handler for the communication with the in-game data aka Openplanet
    """
    def __init__(self):
        # Create the socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('localhost', 50000))
        self.s.settimeout(1.0)

        self._listen_thread = None
        self._state = None
        self.is_listening = False

    def capture(self):
        """
            Create the socket-listening thread
        """      
        if self.is_listening:
            return False

        self.is_listening = True
        # Start the thread
        self._listen_thread = threading.Thread(target=self._capture)
        self._listen_thread.start()

        return True

    def _capture(self):
        """
            Listen to the data sent by the openplanet script on the socket at localhost:50000
        """  
        self.s.listen(1)
        connection = None
        while self.is_listening:
            try:
                connection, addr = self.s.accept()
                while self.is_listening:
                    data = connection.recv(1024).decode("utf-8")
                    if not data:
                        break
                    # This is handling the case where the data is accumulating without a read operation. In that case we use the last parsable message
                    idx2 = data.rfind("}")
                    data = data[:idx2+1]
                    idx1 = data.rfind("{")
                    data = data[idx1:]
                    if idx1 >=0 and idx2 > 0:
                        try:
                            # Update the internal state
                            self._state = json.loads(data)
                        except:
                            print("Couldn't decode packet: ", data)
                    else:
                        print("weird packet going on")
            except socket.timeout:
                pass
            except KeyboardInterrupt:
                break
        # Close the connection
        if connection:
            connection.close()

    def stop(self):
        """
            Stop / Join the listening thread
        """
        if not self.is_listening:
            return False

        self.is_listening = False

        if self._listen_thread is not None:
            self._listen_thread.join(timeout=1)
            self._listen_thread = None
            # Create a new thread ready to start
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind(('localhost', 50000))
            self.s.settimeout(1.0)

        return True

    def getState(self):
        """
            Return the current internal values of the game
        """
        return self._state

    def getTime(self):
        """
            Return the in-game time of the current run
        """
        return self._state["time"]

    def getGameState(self):
        """
            Return a boolean saying if the game is in a game or not (e.g in the menus) 
        """
        return self._state["in_game"]
        
    def isInGame(self):
        """
            Return a boolean saying if the game is in a game or not (e.g in the menus) and not during the countdown at the start. (using the threshold specified in config.py)
        """
        return self._state["in_game"] and self._state["time"] > config.OP_CHRONO_TO_WAIT_BEFORE_PLAYING

    def isGameStateFinish(self):
        """
            Return a boolean saying if the run is in the state where it just crossed the finish line
        """
        return self._state["game_state"] == "Finish"

    def isInGameOrFinish(self):
        """
            Return a boolean saying if it is in an ongoing run  or in the state where it just crossed the finish line
        """
        return self.isInGame() or self.isGameStateFinish()

        