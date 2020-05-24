import os
from BACnetstuff.logMerge import *
from BACnetstuff import pcap
#### TODO: MAIN METHOD SHOULD BE IN UI SKELETON AND SAVE THE DICTIONARIES THERE. ANYTHING THAT USES getUsersDictionary()
#### TODO: SHOULD TAKE IT AS A PARAMETER INSTEAD TO AVOID READING THE SAME FILE OVER AND OVER
#### TODO: MAIN METHOD SHOULD CALL getUsersDictionary AND THEN CREATE A USER OBJECT

# os.getcwd() returns the current working directory
def initialize_Path():
    basepath = os.getcwd().replace("code", "files")
    #for entry in os.listdir(basepath):
    #    if os.path.isfile(os.path.join(basepath, entry)):
    #        return (basepath+"/"+entry)
    #    else:
    #        return -1
    return basepath

def setPath(str):
    return str

# our usersdictionary is a dictionary consisting of usernames as keys and dictionaries as values
# the values are based on the dictionaries returned by logMerge when asked for the current status of feeds

# this function reads the users.txt file to extract the userdictionary so that we can work with it
# returns the read userdictionary
def getUsersDictionary():
    dict = {}
    file = open('users.txt', 'r')
    users = file.read().split('+')
    for user in users:
        feedids = user.split(";")
        dictoffeeds = {}
        for feedid in feedids[1].split(","):
            fid_seqNo = feedid.split(":")
            fid = bytes.fromhex(fid_seqNo[0])
            print("DONE?!")
            dictoffeeds[fid] = int(fid_seqNo[1])
        dict[feedids[0]] = dictoffeeds
    file.close()
    return dict

# this function writes the userdictionary to the user.txt file
# naive implementation always deleting all users before dumping the dictionary again
# no return
def writeUsersDictionary(dict):
    removeAllUsers()
    file = open('users.txt', 'w')
    first = True
    try:
        for name, feed in dict.items():
            user = "" + name + ";"
            firstfeed = True
            for feedID, seqno in feed.items():
                if first:
                    if firstfeed:
                        feedID = feedID.hex()
                        user = user+feedID+":"+str(seqno)
                        firstfeed=False
                    else:
                        feed = feed.hex()
                        user = user+","+feedID+":"+str(seqno)
                else:
                    if firstfeed:
                        feedID = feedID.hex()
                        user = user + feedID + ":" + str(seqno)
                        firstfeed = False
                    else:
                        feed = feedID.hex()
                        user = user + "," + feedID + ":" + str(seqno)
            if not first:
                user="+" + user
            first = False
            file.write(user)
    except KeyError:
        print("keyerror?")

# empties the user.txt file
# no return
def removeAllUsers():
    os.remove('users.txt')
    file = open('users.txt', 'w+')
    file.close()

def removeAllPCAP():
    for file in os.listdir(initialize_Path()):
        try:
            os.remove(file)
        except OSError as e:
            print("Failed to delete %s due to %s", (file, e))

# removes one specified user identified by their username from the user.txt file
# takes username, no return
# TODO: save the dictionary once on starting the program
def removeOneUser(username):
    dictionary = getUsersDictionary()
    if username in dictionary:
        print("Deleted ", username)
        del dictionary[username]
    else:
        print(username, " not found.")
    writeUsersDictionary(dictionary)

# this function returns a dictionary containing information about what events are stored on the device. key is feed id, value is tuple marking from which to which seq_no is stored
# TODO: implement and call where needed (should be only when exporting)
def getStickStatus():
    pass

# class to represent the user that is currently using the software
class User:
    # username is given from the ui
    # usersdictionary is saved between running the program and called via getUsersDictionary
    # currentuserdictionary contains feed_id's as key and latest seq_no's as corresponding values
    def __init__(self, name):
        self.log = LogMerge()
        self.username = name
        self.usersDictionary = getUsersDictionary()
        self.pcapDumpPath = initialize_Path()
        self.updateCurrentUserDictionary()

    # this calls the as of now unimplemented function provided by group 4
    # returns a dictionary of feed_id: seq_no for the current user
    # TODO: insert group 4's method
    def updateCurrentUserDictionary(self):
        self.currentUserDictionary = self.log.get_database_status()
        self.usersDictionary[self.username] = self.currentUserDictionary

    def getSequenceNumbers(self):
        dict = self.usersDictionary
        dict_ = {}
        for user in dict:
            feeds = dict[user]
            for feed in feeds:
                try:
                    if feed in dict_:
                        if dict_[feed] > feeds[feed]:
                            dict_[feed] = feeds[feed]
                    else:
                            dict_[feed] = feeds[feed]
                except KeyError:
                    dict_[feed] = 0
        return dict_

    # This method imports events from the folder on the drive that holds the pcap files created by the export function.
    # returns nothing
    def importing(self):
        self.log.import_logs(self.pcapDumpPath)
        writeUsersDictionary(self.usersDictionary)

    # this method calls the export_logs() function provided by group 4.
    # takes an int specifying the maximum number of events dumped per feed
    # returns nothing
    def exporting(self, maxEvents=30):
        self.importing()
        removeAllPCAP()
        self.log.export_logs(initialize_Path(), self.getSequenceNumbers(), maxEvents)


    # TODO: implement as follows:
    # read every feed and save its sequence number in a dictionary of {feedID:seqNo}
    # then compare it to our sequence numbers getSequenceNumbers() which is also {feedID:seqNo}
    # delete any event that has a lower seqNo than our getSequenceNumbers() returns
    # returns nothing
    def update_dict(self, dictionary):
        pass
if __name__ == '__main__':
    user = User('Patrik')
    user.exporting()