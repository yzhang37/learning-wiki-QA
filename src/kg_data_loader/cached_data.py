import pickle


class CachedData(object):
    def __init__(self, dump_file_name):
        self._out_file = dump_file_name

        try:
            self._data = pickle.load(open(self._out_file, 'rb'))
        except:
            # TODO: more detail error handler
            self._data = dict()

    def __getitem__(self, item):
        raise NotImplementedError()

    def __contains__(self, item):
        return self._data.__contains__(item)

    def dump(self):
        try:
            print("dumping to {}".format(self._out_file))
            pickle.dump(self._data, open(self._out_file, 'wb'))
        except Exception as ex:
            # TODO: more detail error handler
            raise
