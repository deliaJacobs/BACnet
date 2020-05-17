from logStore.database.database_handler import DatabaseHandler as dataBaseHandler
from logStore.funcs.log import create_logger

logger = create_logger('DatabaseConnector')
"""The database connector allows the network layer to access database functionality.

It is meant to be used mostly by logMerge and logSync for their purposes, however, others should feel free to
use it as well.
"""


class DatabaseConnector:
    """Database handler should be implemented by the network connection groups.

    It has the private fields of a database handler to access the necessary database functionality.
    """

    def __init__(self):
        self.__handler = dataBaseHandler()

    def add_event(self, event_as_cbor):
        """"Add a cbor event to the two databases.

        Calls each the byte array handler as well as the event handler to insert the event in both databases
        accordingly. Gets called both by database connector as well as the function connector. Returns 1 if successful,
        otherwise -1 if any error occurred.
        """
        return self.__handler.add_to_db(event_as_cbor)

    def get_current_seq_no(self, feed_id):
        """"Return the current sequence number of a given feed_id, returns an integer with the currently largest
                        sequence number for the given feed. Returns -1 if there is no such feed_id in the database."""
        return self.__handler.get_current_seq_no(feed_id)

    def get_event(self, feed_id, seq_no):
        """"Return a specific cbor event to the callee with the input feed_id and sequence number. Returns None if
                        there is no such entry."""
        return self.__handler.get_event(feed_id, seq_no)

    def get_current_event(self, feed_id):
        """"Return the newest (the one with the highest sequence number) cbor event for a feed_id. Returns None if
                        there is no such feed_id in the database."""
        return self.__handler.get_current_event_as_cbor(feed_id)

    def get_all_feed_ids(self):
        """"Return all current feed ids in the database."""
        return self.__handler.get_all_feed_ids()