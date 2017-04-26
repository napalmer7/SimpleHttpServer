import shelve
import logging
import traceback

logging.basicConfig(level=logging.INFO,
                    format="%(created)-15s %(msecs)d %(levelname)8s %(thread)d %(name)s %(message)s")
logger = logging.getLogger(__name__)


class PendingDataUpdate:
    """Helper class to hold details regarding pending data updates."""
    def __init__(self, key, value, add=True):
        self.key = key
        self.value = value
        self.add = add

    def is_add(self):
        return self.add

    def is_delete(self):
        return not self.add


class SimpleDatastore:
    def __init__(self):
        # Create a reference for the datastore shelve with writeback to allow element updates
        self.datastore = shelve.open("simple_store.sds", writeback=True)
        self.pending_data = []

    def get_data(self, key):
        """Retrieve the data associated with 'key' otherwise None.

        :returns: Value of key or None if not found.
        """
        try:
            return self.datastore[key]
        except:
            return None

    def delete_data(self, key):
        """Delete the key/value pair associated with the supplied key.

        :returns: Value of key or None if not found.
        """
        try:
            data = self.get_data(key)
            logger.error("Found existing data? {}:{}".format(key, data))
            if data:
                # If the key was found, delete it
                self.pending_data.append(PendingDataUpdate(key, data, False))
            return data
        except:
            logger.error("No Found existing data? {}".format(key))
            return None

    def add_pending_item(self, key, value):
        """Add a key/value pair to the pending changes.

        This will overwrite and previous pending data with the same key.

        :returns: bool indicating if this will be an updated item in the datastore
        """
        existing = None
        for x in self.pending_data:
            if x.key == key:
                existing = x
                break

        if existing is not None:
            # Remove any previous pending updates associated with the key
            self.pending_data.remove(x)

        self.pending_data.append(PendingDataUpdate(key, value))

        return key in self.datastore

    def commit_changes(self):
        """Commit all pending changes to the datastore."""
        # Create a local copy
        # If we wanted to support multithreading we could lock here for add
        pending_commits = list(self.pending_data)

        logger.error("Processing {} pending items.".format(len(pending_commits)))

        # clear the pending data
        del self.pending_data[:]

        # multithreading support could free the add lock and have a secondary commit lock here
        for x in pending_commits:
            if x.is_add():
                self.datastore[x.key] = x.value
            else:
                logger.error("Removing key {}".format(x.key))
                try:
                    del self.datastore[x.key]
                except KeyError:
                    # Key error means the key was removed already
                    logger.error("Key error removing key {}".format(x.key))
                    pass
                except Exception as ex:
                    logger.error(traceback.format_exc())
                    logger.error("Unable to delete {}. {}:{}".format(x.key,
                                                                     type(ex),
                                                                     ex))

    def close(self, commit=False):
        """Optionally commit pending data then close the backend datastore.
        """
        try:
            if commit:
                self.commit_changes()
        except Exception as ex:
            logger.error(traceback.format_exc())
            logger.error("Unable to commit pending changes. {}:{}".format(type(ex),
                                                                          ex))

        logger.info("DATA DUMP")
        for k, v in self.datastore.items():
            logger.info("{}:{}".format(k, v))
        self.datastore.close()
