import socket
import json
import threading
import config


class OpenPlanetBridge:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('localhost', 50000))
        self.s.settimeout(1.0)
        self._listen_thread = None
        self._state = None
        self.is_listening = False

    def capture(self):        
        if self.is_listening:
            return False

        self.is_listening = True

        self._listen_thread = threading.Thread(target=self._capture)
        self._listen_thread.start()

        return True

    def _capture(self):
        self.s.listen(1)
        connection = None
        while self.is_listening:
            try:
                connection, addr = self.s.accept()
                while self.is_listening:
                    data = connection.recv(1024).decode("utf-8")
                    if not data:
                        break
                    idx = data.rfind("}")
                    data = data[:idx+1]
                    idx = data.rfind("{")
                    data = data[idx:]
                    self._state = json.loads(data)
            except socket.timeout:
                pass
            except KeyboardInterrupt:
                break
        if connection:
            connection.close()

    def stop(self):
        if not self.is_listening:
            return False

        self.is_listening = False

        if self._listen_thread is not None:
            self._listen_thread.join(timeout=1)
            self._listen_thread = None
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind(('localhost', 50000))
            self.s.settimeout(1.0)

        return True

    def getState(self):
        return self._state

    def getTime(self):
        return self._state["time"]

    def getGameState(self):
        return self._state["in_game"]
        
    def isInGame(self):
        return self._state["in_game"] and self._state["time"] > config.OP_CHRONO_TO_WAIT_BEFORE_PLAYING

    def isGameStateFinish(self):
        return self._state["game_state"] == "Finish"

    def isInGameOrFinish(self):
        return self.isInGame() or self.isGameStateFinish()

        