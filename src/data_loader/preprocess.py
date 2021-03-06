from src.kg_data_loader.wiki_entity import WikiLabel, ValueNotCachedException
import Levenshtein
import src.util.algorithm as algo
from src.util.snippets import CalledProcessError, get_file_lines_quick
from src.adv_types.nerbios import *
import re
import tqdm
from nltk.tokenize import TreebankWordTokenizer


class CustomTreebankWordTokenizer(TreebankWordTokenizer):
    """
    对默认的 nltk.tokenize.TreebankWordTokenizer 做了修改：

    | 原来                  | 现在                                  |
    | --------------------- | ------------------------------------- |
    | 只能分割 ... 的省略号 | 可以分割数量 >=3 的任意长度的省略号。 |
    """
    PUNCTUATION = TreebankWordTokenizer.PUNCTUATION.copy()
    PUNCTUATION[3] = (re.compile(r'(\.{3,})'), r' \1 ')


class NerBX(NerB):
   def __init__(self):
       super().__init__()
       self._label = 'X'


class NerIX(NerI):
   def __init__(self):
       super().__init__()
       self._label = 'X'


class NerEX(NerE):
   def __init__(self):
       super().__init__()
       self._label = 'X'


class NerSX(NerS):
   def __init__(self):
       super().__init__()
       self._label = 'X'


def default_edit_score(str1: str, str2: str):
    """
    缺省的字符串距离比较函数，使用 Levenshtein 编辑距离实现。
    :param str1: 字符串 1
    :param str2: 字符串 2
    :return: 数值，相同为 1.0， 完全不同为 0.0
    """
    max_len = max(len(str1), len(str2))
    return (max_len - Levenshtein.distance(str1, str2)) / max_len


def make_bioes_sequence(fields_list, total_num):
    """
    Given a list, contains a list of tuple, which is each field in a string.
    Make the BIOES sequence.
    :param fields_list: A list of bi-tuple.
    :return: A list of sequence contains B, I, O, E, S element.
    """
    bio_sequence = [NerO() for _ in range(total_num)]

    for pos in fields_list:
        if pos[0] + 1 == pos[1]:
            i, _ = pos
            bio_sequence[i] = NerSX()
        else:
            for i in range(*pos):
                if i == pos[0]:
                    bio_sequence[i] = NerBX()
                elif i == pos[1] - 1:
                    bio_sequence[i] = NerEX()
                else:
                    if bio_sequence[i] == 'O':
                        bio_sequence[i] = NerIX()
    return bio_sequence


def make_bio_sequence(fields_list, total_num):
    """
    Given a list, contains a list of tuple, which is each field in a string.
    Make the BIO sequence
    :param fields_list: A list of bi-tuple.
    :return: A list of sequence contains B, I, O, E, S element.
    """
    bio_sequence = [NerO() for _ in range(total_num)]
    # 转换分区的第一个为 B
    for pos in fields_list:
        for i in range(*pos):
            bio_sequence[i].attribute = 'b' if i == pos[0] else 'i'
    return bio_sequence


def filter_ner_entity(bio_sequence, word_list, func):
    new_word_list = []
    for bio_item, word in zip(bio_sequence, word_list):
        if bio_item == 'O':
            new_word_list.append(word)
        elif func(bio_item):
            new_word_list.append('<e>')
    return new_word_list


def pre_process(
        original_data_file_path: str,
        entity_label: WikiLabel,
        prop_label: WikiLabel,
        output_parsed_source_path: str,
        output_ner_entity_path: str,
        output_log_path: str,
        str_distance_score_handler=default_edit_score,
        dx_range_handler=lambda: range(0, 3),
        float_error_epsilon=1E-08):

    word_tokenizer = CustomTreebankWordTokenizer()

    with open(original_data_file_path, 'r', encoding='utf-8') as fin_orig_data, \
         open(output_parsed_source_path, 'w', encoding='utf-8') as fout_prased_src, \
         open(output_ner_entity_path, 'w', encoding='utf-8') as fout_ner_entity, \
         open(output_log_path, 'w', encoding='utf-8') as fout_error:

        try:
            total_line_count = get_file_lines_quick(original_data_file_path)
        except CalledProcessError:
            total_line_count = None

        for lin_num, line in enumerate(tqdm.tqdm(fin_orig_data, total=total_line_count)):
            # 每次都会得到一个：
            # 主语 id, 属性关系，宾语 id, 查询句子。
            subj, prop, obj, question = line.strip().split('\t')
            question_words = word_tokenizer.tokenize(question)

            ###############
            # 输出使用
            out_line_log = "Ln {0}:".format(lin_num)
            out_line_prased_source = ""
            out_line_ner_segment = ""
            tag_log_has_error = False

            ner_fields = []
            # 遍历（语言，内容）
            for label_wiki_id in (subj, obj):
                try:
                    pos_groups = set()
                    last_min_score = 0.0
                    last_label_word = ""
                    last_label_lang = ""
                    for label_lang, label_word in entity_label[label_wiki_id].items():
                        # 获得对应的语言的 label_word
                        label_word_count = len(label_word.split())

                        # 为了应对 原文中式 Michael B. Macallister，而知识图谱中是 Michael Macallister，
                        # label_word_count 上增加一个 dx 来解决
                        for dx in dx_range_handler():
                            label_word_count_dx = label_word_count + dx

                            for i in range(0, len(question_words) - label_word_count_dx + 1):
                                ngram = ' '.join(question_words[i:i + label_word_count_dx])
                                score = str_distance_score_handler(ngram.lower(), label_word.lower())

                                if score > 0 + float_error_epsilon and (len(pos_groups) == 0 or score >= last_min_score - float_error_epsilon):
                                    if score > last_min_score + float_error_epsilon:
                                        pos_groups.clear()
                                        last_label_word = label_word
                                        last_label_lang = label_lang
                                    if label_lang == last_label_lang:
                                        pos_groups.add((i, i + label_word_count_dx))
                                        last_min_score = score

                    if len(pos_groups) > 0:
                        pos_groups = algo.merge_position_tuples(pos_groups)
                        if last_min_score >= 0.80:
                            # 可以设置一定大小的阈值
                            for pos in pos_groups:
                                ner_fields.append((
                                    pos, last_min_score, ' '.join(question_words[slice(*pos)]), last_label_word))

                except ValueNotCachedException:
                    out_line_log += " | entity '{0}' value not cached".format(label_wiki_id)
                    tag_log_has_error = True

            if len(ner_fields) > 0:
                # if len(ner_fields) > 1:
                #     output_sentences.append("-- {0} fields found --".format(len(ner_fields)))

                # 寻找其中的特殊范围
                bio_pos_list = []
                for pos, score, in_word, label_word in ner_fields:
                    out_line_log += " | “{0}” {2:.2f} “{1}”".format(in_word, label_word, score)
                    bio_pos_list.append(pos)

                bio_pos_list = algo.merge_position_tuples(bio_pos_list)
                bio_sequence = make_bioes_sequence(bio_pos_list, len(question_words))

                # 输出根据 sequence，filtered 后的单词
                bio_filter_words = filter_ner_entity(bio_sequence, question_words, lambda x: x == 'B' or x == 'S')
                out_line_prased_source = ' '.join(bio_filter_words)
                out_line_ner_segment = '\n'.join([
                    "{0} {1}".format(word, ner_e) for word, ner_e in zip(question_words, bio_sequence)
                ])

            else:
                out_line_log += " | no entity recognized or low confidence"
                tag_log_has_error = True

            if not tag_log_has_error:
                out_line_log += " | OK"
                out_line_ner_segment += "\n"
            else:
                out_line_prased_source = ""
                out_line_ner_segment = ""

            fout_error.write(out_line_log + '\n')
            fout_ner_entity.write(out_line_ner_segment + '\n')
            fout_prased_src.write(out_line_prased_source + '\n')
