import pickle
import sys


class CachedDataException(Exception):
    pass


class CachedData(object):
    def __init__(self, dump_file_name):
        self._out_file = dump_file_name
        self._to_save = False
        self._data = dict()
        try:
            self._data = pickle.load(open(self._out_file, 'rb'))
        except FileNotFoundError:
            print("create new cached data for {0}".format(self._out_file), file=sys.stderr)
        except pickle.PickleError:
            print("failed to load from {0}. Empty object use instead.".format(self._out_file), file=sys.stderr)
        except Exception as ex:
            print("unexcepted error when loading from {0}.".format(self._out_file), file=sys.stderr)
            print(ex, file=sys.stderr)
            print("Empty object use instead.", file=sys.stderr)

    def __getitem__(self, item):
        raise NotImplementedError()

    def __contains__(self, item):
        return self._data.__contains__(item)

    def dump(self):
        try:
            print("dumping to {}".format(self._out_file))
            pickle.dump(self._data, open(self._out_file, 'wb'))
            self._to_save = False
        except Exception as ex:
            # TODO: more detail error handler
            raise

    def __del__(self):
        if self._to_save:
            print("warning: cached data {0} have unsaved changes".format(self._out_file), file=sys.stderr)
