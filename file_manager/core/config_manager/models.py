

class Config():
    def __init__(self, name, date, ver, path, id=None, attributes=None, special=None):
        self.id = id
        self.name = name
        self.date = date
        self.ver = ver
        self.path = path
        self.attributes = attributes
        self.special = special

    def __repr__(self):
        return f'Config:\n\tid={self.id}\n\tname={self.name}\n\tdate={self.date}\n\tver={self.ver}\n\tpath={self.path}\n\t{self.attributes}'
