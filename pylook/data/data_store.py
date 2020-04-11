class DataStore:
    """Class singleton
    """

    instance = None

    def __init__(self):
        if DataStore.instance is None:
            DataStore.instance = DataStore.__DataStore()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name):
        return setattr(self.instance, name)

    class __DataStore:

        __slots__ = (
            'filenames',
            )

        def __init__(self):
            self.filenames = list()
        
        def add_file(self, filename):
            self.filenames.append(filename)
        
        def add_files(self, filenames):
            self.filenames.extend(filenames)
        
        @property
        def files(self):
            return self.filenames
            