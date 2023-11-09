#Achievements and data
USERFILE = 'media/user.txt'

class UserData:
    def __init__(self) -> None:
        self.user_data = self.load_user_data()

    def load_user_data(self):
        with open(USERFILE, 'r') as userFile:
            userdata = {
                "name": "Guest",
                "bestScore": 0,
                "numVictories": 0,
                "numGames": 0
            }
            for i, line in enumerate(userFile):
                line = line.rstrip()
                if i == 0:
                    userdata["name"] = line
                elif i == 1:
                    userdata["bestScore"] = int(line)
                elif i == 2:
                    userdata["numVictories"] = int(line)
                elif i == 3:
                    userdata["numGames"] = int(line)
        return userdata
    
    def save_user_data(self, user_data):
        with open(USERFILE, 'w') as userFile:
            userFile.write(str(user_data.get("name", "Guest")) + "\n")
            userFile.write(str(user_data.get("bestScore", 0)) + "\n")
            userFile.write(str(user_data.get("numVictories", 0)) + "\n")
            userFile.write(str(user_data.get("numGames", 0)) + "\n")

    def increase_gameplay(self):
        user_data = self.load_user_data()
        user_data["numGames"] += 1
        self.save_user_data(user_data)     
        self.user_data = user_data
            
    def get_user_data(self):
        return self.user_data