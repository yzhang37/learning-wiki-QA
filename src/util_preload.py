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
                                e, os.path.split(file_name)[1], the_tqdm.n+1))
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
                            prop, os.path.split(file_name)[1], the_tqdm.n+1))
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


if __name__ == "__main__":
    preload_given_list(data=["Q7370831", "P738", "Q5718236", "Q9052447", "Q7736435", "Q2735971", "Q12042559", "Q5605195",
                             "Q16960484", "Q4105939", "Q6953752", "Q4942271", "Q12770348", "Q9387475", "Q4647166",
                             "Q3216572", "Q3788096", "Q3050585", "Q20669641", "Q7233382", "Q6103747", "Q16237671",
                             "Q6753606", "Q12589288", "Q16223812", "Q12599326", "Q18098515", "Q14906023", "Q12966187",
                             "Q7488898", "Q7964387", "Q6394424", "Q6692583", "Q7248129", "Q5039028", "Q5706870", "Q5598420",
                             "Q3361944", "Q5700638", "Q5194891", "Q7409185", "Q7126634", "Q11273974", "Q6974068", "Q192142",
                             "Q7732189", "Q11775418", "Q4838360", "Q8070167", "Q15818195", "Q16252092", "Q6410036",
                             "Q7091200", "Q11707850", "Q4820757", "Q14404931", "Q12220723", "Q7382530", "Q4338862",
                             "Q3431119", "Q4859075", "Q6932988", "Q14917911", "Q7596477", "Q5297452", "Q4321732",
                             "Q3235173", "Q15059374", "Q3378062", "Q15033015", "Q16148864", "Q5331232", "Q13403424",
                             "Q7838078", "Q15982550", "Q7331173", "Q2822934", "Q5652774", "Q16195732", "Q16080769",
                             "Q7346247", "Q3045848", "Q6404502", "Q4641098", "Q19599860", "Q4773431", "Q6888475",
                             "Q5221052", "Q57312", "Q12814938", "Q16223278", "Q7645830", "Q18780030", "Q4963579",
                             "Q17074635", "Q4872068", "Q2223419", "Q19953755", "Q2618383", "Q4904491", "Q3037455",
                             "Q7421648", "Q5269278", "Q19572184", "Q6986428", "Q5054679", "Q4299693", "Q3925903",
                             "Q16729889", "Q4332612", "Q4703716", "Q7088228", "Q3931524", "Q12302219", "Q5279580",
                             "Q7669690", "Q5689455", "Q7745029", "Q8037752", "Q10371036", "Q5089493", "Q3393521",
                             "Q2549305", "Q1699115", "Q7759854", "Q7995397", "Q5057342", "Q3020776", "Q157180",
                             "Q46299", "Q1709703", "Q7186160", "Q930143", "Q7597674", "Q7381169", "Q2713775",
                             "Q19573383", "Q17093672", "Q7761836", "Q15220429", "Q6415212", "Q5317572", "Q1379", "Q6510436",
                             "Q19668190", "Q7801242", "Q5112710", "Q14762987", "Q16225648", "Q5147070", "Q7882442",
                             "Q7486033", "Q7416309", "Q3621869", "Q5396932", "Q4299829", "Q7679269", "Q5275474",
                             "Q17010897", "Q7262848", "Q7462924", "Q4358240", "Q17104673", "Q2359457", "Q7680553",
                             "Q18126107", "Q2091526", "Q7169620", "Q5478675", "Q11694964", "Q7353482", "Q7740464",
                             "Q18276118", "Q2943336", "Q5205412", "Q5642292", "Q5825618", "Q3561596", "Q7294904",
                             "Q5975793", "Q1094966", "Q18678866", "Q15027402", "Q7611263", "Q12136334", "Q3567716",
                             "Q13860490", "Q342268", "Q4606351", "Q7514676", "Q17009350", "Q5689596", "Q7490667",
                             "Q7361197", "Q4728706", "Q12970119", "Q4356186", "Q13554171", "Q16059357", "Q10367240",
                             "Q17098977", "Q3202866", "Q7549549", "Q15039612", "Q7849560", "Q5237124", "Q7897089",
                             "Q16249633", "Q5205482", "Q2102493", "Q16253560", "Q7677888", "Q6476835", "Q600355",
                             "Q11634794", "Q15021043", "Q2998279", "Q6983152", "Q6225463", "Q5608784", "Q5300232",
                             "Q5039383", "Q8053490", "Q18420748", "Q2007609", "Q7750757", "Q16961386", "Q7877290",
                             "Q16223698", "Q3869374", "Q1967337", "Q5302873", "Q10396284", "Q7194867", "Q3434066",
                             "Q20195163", "Q3132537", "Q11836302", "Q3048496", "Q8774954", "Q16666103", "Q7623237",
                             "Q6832738", "Q3986708", "Q5596265", "Q7334947", "Q16145275", "Q3868545", "Q4770380",
                             "Q4115193", "Q10381849", "Q5085769", "Q3816698", "Q3246900", "Q7383026", "Q7033597",
                             "Q7262851", "Q7713650", "Q5730666", "Q5220157"])
