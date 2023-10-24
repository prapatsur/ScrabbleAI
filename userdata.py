#Achievements and data
USERFILE = 'media/user.txt'

class UserData:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self) -> None:
        self.user_data = self.load_user_data()

    def load_user_data(self):
        userFile = open(USERFILE, 'r')
        i = 0
        userdata = {}
        userdata["name"] = "Guest"
        userdata["bestScore"] = 0
        userdata["numVictories"] = 0
        userdata["numGames"] = 0
        for line in userFile:
            line = line.rstrip()
            if i == 0:
                userdata["name"] = line
            elif i == 1:
                userdata["bestScore"] = int(line)
            elif i == 2:
                userdata["numVictories"] = int(line)
            elif i == 3:
                userdata["numGames"] = int(line)
                
            i += 1
                
        return userdata