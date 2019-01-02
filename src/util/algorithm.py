

def merge_position_tuples(dat: iter):
    """
    给定一序列的 Tuple, 仅将完全闭合的元组进行合并。
    :param dat: an iterable groups of bi-tuples
    :return: an list with merged bi-tuples
    """
    posgrp = sorted(set(dat))
    cleaner = [0] * len(posgrp)
    retgrp = []

    explorer = 1
    worker = 0

    def find_next(it: list, v, beg, default):
        try:
            return it.index(v, beg)
        except:
            return default

    while worker < len(posgrp):
        if explorer >= len(posgrp) or posgrp[explorer][0] >= posgrp[worker][1]:
            # explorer 到头了，或者 explorer 的元素完全在当前的后侧
            retgrp.append(posgrp[worker])
            cleaner[worker] = 1
            worker = find_next(cleaner, 0, worker, len(cleaner))
            explorer = find_next(cleaner, 0, worker + 1, len(cleaner))
        elif posgrp[explorer][0] > posgrp[worker][0]:
            if posgrp[explorer][1] <= posgrp[worker][1]:
                cleaner[explorer] = 1
            explorer = find_next(cleaner, 0, explorer + 1, len(cleaner))
        else: # posgrp[explorer][0] == posgrp[worker][0]
            # 因为去重且排序过，explorer[1] 一定 > worker[1]
            worker = explorer
            cleaner[explorer] = 1
            explorer = find_next(cleaner, 0, explorer + 1, len(cleaner))
    return retgrp

