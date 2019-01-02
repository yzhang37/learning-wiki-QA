import requests
import ujson as json
from src.kg_data_loader.cached_data import CachedData, CachedDataException


class ReadOnlyProtected(CachedDataException):
    pass


class ValueNotCachedException(ReadOnlyProtected):
    pass


class WikiLabel(CachedData):
    def __init__(self, dump_file_name, is_read_only: bool=False):
        super().__init__(dump_file_name)
        self._read_only = is_read_only

    @property
    def read_only(self):
        return self._read_only

    @read_only.setter
    def read_only(self, value: bool):
        self._read_only = value

    def _get_entity_data(self, item: str):
        if self.read_only:
            raise ReadOnlyProtected
        # TODO: check the validity of item name
        try:
            ret = requests.get("http://www.wikidata.org/entity/{0}".format(item))
            ret.raise_for_status()
            ret_data = json.loads(ret.text)
            ret_data = ret_data['entities']
            if item in ret_data:
                ret_data = ret_data[item]['labels']
            elif len(ret_data) == 1:
                new_item = list(ret_data.keys())[0]
                if new_item != item:
                    raise Exception("{0}\t->\t{1}".format(item, new_item))
            else:
                raise Exception("error: {}".format(item))
            self._data[item] = {lang: item['value'] for lang, item in ret_data.items()}
            self._to_save = True
        except Exception as ex:
            self._data[item] = None
            raise
        return self._data[item]

    def invalidate(self, item: str):
        if item in self._data:
            if self.read_only:
                raise ReadOnlyProtected
            del self._data[item]

    def __getitem__(self, item: str):
        if item in self._data:
            if self._data[item] is None:
                raise ValueNotCachedException
            return self._data[item]
        else:
            if self.read_only:
                raise ValueNotCachedException
            return self._get_entity_data(item)
