import requests
import ujson as json
from src.cached_data import CachedData


class WikiLabel(CachedData):
    def __init__(self, dump_file_name):
        super().__init__(dump_file_name)

    def _get_entity_data(self, item: str):
        # check the validity of item name
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
        except Exception as ex:
            self._data[item] = None
            raise
        return self._data[item]

    def invalidate(self, item: str):
        if item in self._data:
            del self._data[item]

    def __getitem__(self, item: str):
        if item in self._data:
            return self._data[item]
        else:
            return self._get_entity_data(item)
