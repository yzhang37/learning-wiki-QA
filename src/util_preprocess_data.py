from src.data_loader.preprocess import pre_process
from src.kg_data_loader.wiki_entity import WikiLabel
from src.config import BaseConfig
from src.util.snippets import unzip_dict

config = BaseConfig()

# 字典抽取函数
# dat_unzip = lambda x: unzip_dict(x, "train", "valid", "test")
dat_unzip = lambda x: unzip_dict(x, "test")


dat_list = [
    config.FILE_DATA_WD_ORIGIN,
    config.FILE_PROCESSED_WD_PRASED,
    config.FILE_LOGS_WD_PREPROCESS_STATUS
]

wiki_entity_label = WikiLabel(config.FILE_DUMP_WD_ENTITY_LABEL, is_read_only=True)
wiki_property_label = WikiLabel(config.FILE_DUMP_WD_PROP_LABEL, is_read_only=True)

tulips = tuple(map(dat_unzip, dat_list))
for orig_data, parsed_src, err_log in zip(*tulips):
    pre_process(
        orig_data,
        wiki_entity_label,
        wiki_property_label,
        parsed_src,
        err_log
    )
