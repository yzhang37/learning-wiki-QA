__all__ = ["NerB", "NerI", "NerO", "NerE", "NerS"]


class NerEntity:
    def __init__(self):
        self._attrib = 'o'
        self._label = ""

    @property
    def attribute(self):
        return self._attrib.upper()

    @attribute.setter
    def attribute(self, value: str):
        if not len(value) == 1:
            raise ValueError("should contain only 1 char.")
        self._attrib = value.lower()

    @property
    def label(self):
        return self._label.upper()

    @label.setter
    def label(self, value: str):
        self._label = value.strip()

    def __eq__(self, other):
        if isinstance(other, NerEntity):
            return self.attribute == other.attribute
        else:
            return self.attribute == str(other)

    def __str__(self):
        return "{0}{1}".format(self.attribute, "-" + self.label if len(self._label) > 0 else "")

    def __repr__(self):
        return "<{}>".format(self.__str__())


class NerB(NerEntity):
    def __init__(self):
        super().__init__()
        self._attrib = 'b'


class NerI(NerEntity):
    def __init__(self):
        super().__init__()
        self._attrib = 'i'


class NerO(NerEntity):
    pass


class NerE(NerEntity):
    def __init__(self):
        super().__init__()
        self._attrib = 'e'


class NerS(NerEntity):
    def __init__(self):
        super().__init__()
        self._attrib = 's'
