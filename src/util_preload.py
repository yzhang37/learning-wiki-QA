import os
import tqdm
import time
import sys
from src.config import BaseConfig
from src.wiki_entity import WikiLabel

# 配置信息
config = BaseConfig()

# 实体标签
entity_label = WikiLabel(config.FILE_DUMP_WD_ENTITY_LABEL)
property_label = WikiLabel(config.FILE_DUMP_WD_PROP_LABEL)


# 预加载所有的实体名称
def __preload():
    fil_preload_faillist = open(config.FILE_LOGS_WD_FAILLIST, 'w', encoding='utf-8')

    fil_preload_logs = open(config.FILE_LOGS_WD_PRELOAD, 'a+', encoding='utf-8')
    fil_preload_logs.write("\nstarted at {0}\n".format(time.asctime()))
    fil_preload_logs.flush()

    for file_name in config.FILE_DATA_WD_ORIGIN.values():
        total_lines = int(os.popen("wc -l {0}".format(file_name)).read().strip().split()[0])
        the_tqdm = tqdm.tqdm(total=total_lines)
        with open(file_name, 'r', encoding='utf-8') as fin:
            for line in fin:
                e1, prop, e2, _ = line.split('\t')

                for e in (e1, e2):
                    if e not in entity_label:
                        try:
                            ret = entity_label[e]
                        except Exception as ex:
                            fil_preload_faillist.write("{}\tEntity\tin {}, ln {}\n".format(
                                e, os.path.split(file_name)[1], the_tqdm.n + 1))
                            fil_preload_faillist.flush()
                            fil_preload_logs.write("{}\n".format(ex))
                            fil_preload_logs.flush()

                if prop[0] == 'R':
                    prop = 'P' + prop[1:]

                if prop not in property_label:
                    try:
                        ret = property_label[prop]
                    except Exception as ex:
                        fil_preload_faillist.write("{}\tProp\tin {}, ln {}\n".format(
                            prop, os.path.split(file_name)[1], the_tqdm.n + 1))
                        fil_preload_faillist.flush()
                        fil_preload_logs.write("{}\n".format(ex))
                        fil_preload_logs.flush()

                the_tqdm.update()

                if the_tqdm.n % 1000 == 0:
                    entity_label.dump()
                    property_label.dump()

        the_tqdm.close()
        entity_label.dump()
        property_label.dump()
    fil_preload_faillist.close()


# 可以通过命令行来访问
def preload_given_list(data: list):
    fil_preload_fail = open(config.FILE_LOGS_WD_FAILLIST, 'w', encoding='utf-8')
    fil_preload_logs = open(config.FILE_LOGS_WD_PRELOAD, 'a+', encoding='utf-8')
    fil_preload_logs.write("\nstarted at {0}\n".format(time.asctime()))
    fil_preload_logs.flush()
    for item_name in tqdm.tqdm(data):
        if item_name[0] == 'Q':
            # 实体
            if item_name not in entity_label or entity_label[item_name] is None:
                try:
                    entity_label.invalidate(item_name)
                    ret = entity_label[item_name]
                except Exception as ex:
                    fil_preload_fail.write("{}\tEntity\n".format(item_name))
                    fil_preload_fail.flush()
                    fil_preload_logs.write("{}\n".format(ex))
                    fil_preload_logs.flush()
        elif item_name[0] == 'P':
            # 关系
            if item_name not in property_label or property_label[item_name] is None:
                try:
                    property_label.invalidate(item_name)
                    ret = property_label[item_name]
                except Exception as ex:
                    fil_preload_fail.write("{}\tProp\n".format(item_name))
                    fil_preload_fail.flush()
                    fil_preload_logs.write("{}\n".format(ex))
                    fil_preload_logs.flush()
        else:
            fil_preload_fail.write("{0}\tInvalid type\n".format(item_name))
            fil_preload_fail.flush()
    entity_label.dump()
    property_label.dump()
    fil_preload_fail.close()

