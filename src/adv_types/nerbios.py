__all__ = ["NerB", "NerI", "NerO"]


class NerEntity:
    def __init__(self, attrib=None):
        self._attrib = attrib

    @property
    def attribute(self):
        if self._attrib is None:
            return "O"
        if self._attrib == 'b':
            return 'B'
        elif self._attrib == 'i':
            return 'I'
        else:
            return 'undef'

    @attribute.setter
    def attribute(self, value: str):
        if not len(value) == 1:
            raise ValueError("should contain only 1 char.")
        self._attrib = value.lower()

    def __eq__(self, other):
        if isinstance(other, NerEntity):
            return self.attribute == other.attribute
        else:
            return self.attribute == str(other)

    def __repr__(self):
        return "<{}>".format(self.attribute)


class NerB(NerEntity):
    def __init__(self):
        super().__init__('b')


class NerI(NerEntity):
    def __init__(self):
        super().__init__('i')


class NerO(NerEntity):
    pass

