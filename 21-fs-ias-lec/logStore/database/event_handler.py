import pickle

from ..funcs.singleton import Singleton
from .sql_alchemy_connector import SqLiteDatabase
from ..funcs.constants import SQLITE
from ..funcs.event import Event
from ..funcs.log import create_logger

logger = create_logger('EventHandler')

connPep = {}


class EventHandler(metaclass=Singleton):

    def __init__(self):
        self.__sqlAlchemyConnector = SqLiteDatabase(SQLITE, dbname='eventDatabase.sqlite')
        self.__sqlAlchemyConnector.create_chat_event_table()
        self.__sqlAlchemyConnector.create_kotlin_table()
        self.__sqlAlchemyConnector.create_master_table()

    def add_event(self, event_as_cbor):
        try:
            event = Event.from_cbor(event_as_cbor)
            seq_no = event.meta.seq_no
            feed_id = event.meta.feed_id
            content = event.content.content

            cont_ident = content[0].split('/')
            application = cont_ident[0]
            application_action = cont_ident[1]

            if application == 'chat':
                if application_action == 'MASTER':
                    return

                elif application_action =='sendName':
                    newName = content[1]['name']

                    username_file = open("username.pkl", 'rb')
                    username_dict = pickle.load(username_file)
                    username_file.close()

                    if not newName == username_dict['username']:
                        file = open('connectedPerson.pkl', 'rb')
                        connPep = pickle.load(file)
                        file.close()
                        alreadyExists = False

                        for entry in connPep:
                            if entry == newName:
                                alreadyExists = True
                                break

                        if not alreadyExists:
                            connPep[newName] = newName
                            file = open('connectedPerson.pkl', 'wb')
                            pickle.dump(connPep, file)
                            file.close()

                elif application_action == 'MyNameChanged':

                    username_file = open("username.pkl", 'rb')
                    username_dict = pickle.load(username_file)
                    username_file.close()

                    if not content[1]['fromUser'] == username_dict['username']:

                        f = open('connectedPerson.pkl', 'rb')
                        entries = pickle.load(f)
                        f.close()

                        for entry in entries:
                            # entry[0] = key for specific entry, content[1]['fromUser'] = oldUsername
                            if entry == content[1]['fromUser']:
                                # there is no nickname for this person
                                if entry == entries[entry]:
                                    entries[content[1]['newName']] = content[1]['newName']
                                    entries.pop(entry)
                                    break
                                else:
                                    # there is a nickname for this person
                                    entries[content[1]['newName']] = entries[content[1]['fromUser']]
                                    entries.pop(entry)
                                    break

                        f = open('connectedPerson.pkl', 'wb')
                        pickle.dump(entries, f)
                        f.close()

                        # update personlist.pkl:
                        f = open('personList.pkl', 'rb')
                        person = pickle.load(f)
                        f.close()

                        for i in range(len(person)):
                            if person[i][0] == content[1]['fromUser']:
                                person[i][0] = content[1]['newName']

                        f = open('personList.pkl', 'wb')
                        pickle.dump(person, f)
                        f.close()

                elif application_action == 'nameChanged':

                    print("nameChanged Event")

                    #Someone gave me a nickname
                    newName = content[1]['newName']
                    fromUser = content[1]['fromUser']
                    # only add the name if fromUser is not you:
                    # therefor use username.pkl
                    username_file = open("username.pkl", 'rb')
                    username_dict = pickle.load(username_file)
                    username_file.close()

                    if not fromUser == username_dict['username']:

                        nameAcceptable = True

                        file = open("unwantedNames.txt", 'r')
                        names = file.readlines()

                        for name in names:
                            name = name.replace("\n", "")

                            if newName.lower().find(name.lower()) != -1:
                                nameAcceptable = False
                                break
                        file.close()

                        # add new name to txt, names slpi wi
                        my_names_file = open("my_names.txt", 'a')

                        if nameAcceptable == True:
                            my_names_file.write(newName + ", ")
                            my_names_file.close()
                            print("name is acceptable")

                            file = open('resetName.txt', 'w')
                            file.write("False")
                            file.close()


                        else:

                            oldName = content[1]['oldFriendsUsername']
                            file = open('resetName.txt', 'w')
                            file.write("True/"+newName+"/"+oldName+"/"+fromUser)
                            file.close()

                            """
                            print("createUnwantedEvent Aufruf")
                            #createUnwantedEvent(newName, fromUser, content[1]['oldName'])
                            ecf = EventFactory()
                            unwantedNameEvent = ecf.next_event('chat/unwantedName',{'name': newName, 'fromUser': fromUser,'oldName': content[1]['oldFriendsUsername'] })
                            chat_function = ChatFunction()
                            chat_function.insert_event(unwantedNameEvent)

                            """

                elif application_action == 'unwantedName':

                    print("unwantedName Methode wird ausgeführt")

                    username_file = open("username.pkl", 'rb')
                    username_dict = pickle.load(username_file)
                    username_file.close()

                    print(content[1]['fromUser'])
                    print(username_dict['username'])

                    if (content[1]['fromUser'] == username_dict['username']):
                        print("why??")

                        with open('connectedPerson.pkl', 'rb') as f:
                            file = pickle.load(f)
                        f.close()

                        key = ''
                        items = file.items()
                        for t in items:
                            if t[1] == content[1]['name']:
                                key = t[0]

                        file[key] = content[1]['oldName']

                        f = open('connectedPerson.pkl', 'wb')
                        pickle.dump(file, f)
                        f.close()


                else:
                    chatMsg = content[1]['messagekey']
                    chat_id = content[1]['chat_id']
                    timestamp = content[1]['timestampkey']

                    self.__sqlAlchemyConnector.insert_event(feed_id=feed_id, seq_no=seq_no, application=application,
                                                            chat_id=chat_id,
                                                            timestamp=timestamp, data=chatMsg)


            elif application == 'KotlinUI':
                if application_action == 'post':
                    username = content[1]['username']
                    timestamp = content[1]['timestamp']
                    text = content[1]['text']
                    self.__sqlAlchemyConnector.insert_kotlin_event(feed_id=feed_id, seq_no=seq_no,
                                                                   application=application_action,
                                                                   username=username, oldusername='',
                                                                   timestamp=timestamp, text=text)

                elif application_action == 'username':
                    username = content[1]['newUsername']
                    oldusername = content[1]['oldUsername']

                    timestamp = content[1]['timestamp']
                    self.__sqlAlchemyConnector.insert_kotlin_event(feed_id=feed_id, seq_no=seq_no,
                                                                   application=application_action,
                                                                   username=username, oldusername=oldusername,
                                                                   timestamp=timestamp, text='')

            elif application == 'MASTER':
                self.master_handler(seq_no, feed_id, content, cont_ident, event_as_cbor)

            else:
                raise InvalidApplicationError('Invalid application called %s' % application)
        except KeyError as e:
            logger.error(e)
            return -1

    def get_event_since(self, application, timestamp, chat_id):
        return self.__sqlAlchemyConnector.get_all_events_since(application, timestamp, chat_id)

    def get_all_events(self, application, chat_id):
        return self.__sqlAlchemyConnector.get_all_event_with_chat_id(application, chat_id)

    def get_Kotlin_usernames(self):
        return self.__sqlAlchemyConnector.get_all_usernames()

    def get_all_kotlin_events(self):
        return self.__sqlAlchemyConnector.get_all_kotlin_events()

    def get_all_entries_by_feed_id(self, feed_id):
        return self.__sqlAlchemyConnector.get_all_entries_by_feed_id(feed_id)

    def get_last_kotlin_event(self):
        return self.__sqlAlchemyConnector.get_last_kotlin_event()

    """"Structure of insert_master_event:
    insert_master_event(self, master, feed_id, app_feed_id, trust_feed_id, seq_no, trust, name, radius, event_as_cbor, app_name)"""

    def master_handler(self, seq_no, feed_id, content, cont_ident, event_as_cbor):
        """Handle master events and insert the events corresponding to their definition:"""
        event = cont_ident[1]
        if event == 'MASTER':
            self.__sqlAlchemyConnector.insert_master_event(True, feed_id, None, None, seq_no, None, None, 0,
                                                           event_as_cbor, None)
        elif event == 'Trust':
            self.__sqlAlchemyConnector.insert_master_event(False, feed_id, None, content[1]['feed_id'], seq_no, True,
                                                           None, None, event_as_cbor, None)
            from feedCtrl.radius import Radius
            r = Radius()
            r.calculate_radius()
        elif event == 'Block':
            self.__sqlAlchemyConnector.insert_master_event(False, feed_id, None, content[1]['feed_id'], seq_no, False,
                                                           None, None, event_as_cbor, None)
            from feedCtrl.radius import Radius
            r = Radius()
            r.calculate_radius()
        elif event == 'Name':
            self.__sqlAlchemyConnector.insert_master_event(False, feed_id, None, None, seq_no, None,
                                                           content[1]['name'], None, event_as_cbor, None)
        elif event == 'NewFeed':
            self.__sqlAlchemyConnector.insert_master_event(False, feed_id, content[1]['feed_id'], None, seq_no, True,
                                                           None, None, event_as_cbor, content[1]['app_name'])
        elif event == 'Radius':
            self.__sqlAlchemyConnector.insert_master_event(False, feed_id, None, None, seq_no,
                                                           None, None, content[1]['radius'], event_as_cbor, None)
        elif event == 'ReportName':
            file = open("connectedPerson.txt", "a")
            file.write("\n")
            print("event handler " + content[1]['trustedName'])
            file.write(content[1]['trustedName'])
            file.close()
        else:
            raise InvalidApplicationError('Invalid action called %s' % event)

    """"Following come the feed control mechanisms used by database_handler:"""

    def get_trusted(self, master_id):
        return self.__sqlAlchemyConnector.get_trusted(master_id)

    def get_blocked(self, master_id):
        return self.__sqlAlchemyConnector.get_blocked(master_id)

    def get_all_master_ids(self):
        return self.__sqlAlchemyConnector.get_all_master_ids()

    def get_all_master_ids_feed_ids(self, master_id):
        return self.__sqlAlchemyConnector.get_all_master_ids_feed_ids(master_id)

    def get_username(self, master_id):
        return self.__sqlAlchemyConnector.get_username(master_id)

    def get_my_last_event(self):
        return self.__sqlAlchemyConnector.get_my_last_event()

    def get_host_master_id(self):
        return self.__sqlAlchemyConnector.get_host_master_id()

    def get_radius(self):
        return self.__sqlAlchemyConnector.get_radius()

    def get_master_id_from_feed(self, feed_id):
        return self.__sqlAlchemyConnector.get_master_id_from_feed(feed_id)

    def get_application_name(self, feed_id):
        return self.__sqlAlchemyConnector.get_application_name(feed_id)

    def get_feed_ids_from_application_in_master_id(self, master_id, application_name):
        return self.__sqlAlchemyConnector.get_feed_ids_from_application_in_master_id(master_id, application_name)

    def get_feed_ids_in_radius(self):
        return self.__sqlAlchemyConnector.get_feed_ids_in_radius()

    def set_feed_ids_radius(self, feed_id, radius):
        return self.__sqlAlchemyConnector.set_feed_ids_radius(feed_id, radius)


class InvalidApplicationError(Exception):
    def __init__(self, message):
        super(InvalidApplicationError, self).__init__(message)

