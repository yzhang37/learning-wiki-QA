
class BaseConfig:
    def __init__(self):
        import os
        pjoin = os.path.join
        psplit = os.path.split
        pabs = os.path.abspath

        self.PATH_BASE = pabs(pjoin(psplit(__file__)[0], ".."))
        self.PATH_DATA = pabs(pjoin(self.PATH_BASE, "data"))
        self.PATH_PROCESSED = pabs(pjoin(self.PATH_BASE, "processed_data"))
        self.PATH_DUMP = pabs(pjoin(self.PATH_BASE, "dump"))
        self.PATH_LOGGING = pabs(pjoin(self.PATH_BASE, "logs"))

        self.FILE_DATA_WD_ORIGIN = {
            "train": pabs(pjoin(self.PATH_DATA, "annotated_wd_data_train.txt")),
            "test": pabs(pjoin(self.PATH_DATA, "annotated_wd_data_test.txt")),
            "valid": pabs(pjoin(self.PATH_DATA, "annotated_wd_data_valid.txt"))
        }

        self.FILE_PROCESSED_WD_PRASED = {
            "train": pabs(pjoin(self.PATH_PROCESSED, "prased_source_train.txt")),
            "test": pabs(pjoin(self.PATH_PROCESSED, "prased_source_test.txt")),
            "valid": pabs(pjoin(self.PATH_PROCESSED, "prased_source_valid.txt"))
        }

        self.FILE_PROCESSED_ENTITY_BIOES = {
            "train": pabs(pjoin(self.PATH_PROCESSED, "ner_tag_train.bmes")),
            "test": pabs(pjoin(self.PATH_PROCESSED, "ner_tag_test.bmes")),
            "valid": pabs(pjoin(self.PATH_PROCESSED, "ner_tag_valid.bmes"))
        }

        self.FILE_DUMP_WD_ENTITY_LABEL = pabs(pjoin(self.PATH_DUMP, "wd_entity_label.pickle"))
        self.FILE_DUMP_WD_PROP_LABEL = pabs(pjoin(self.PATH_DUMP, "wd_prop_label.pickle"))

        self.FILE_LOGS_WD_PRELOAD = pabs(pjoin(self.PATH_LOGGING, "wd_preload.log"))
        self.FILE_LOGS_WD_FAILLIST = pabs(pjoin(self.PATH_LOGGING, "wd_fail.txt"))
        self.FILE_LOGS_WD_PREPROCESS_STATUS = {
            "train": pabs(pjoin(self.PATH_LOGGING, "preproc_status_train.log")),
            "test": pabs(pjoin(self.PATH_LOGGING, "preproc_status_test.log")),
            "valid": pabs(pjoin(self.PATH_LOGGING, "preproc_status_valid.log"))
        }