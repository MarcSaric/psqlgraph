from util import sanitize


class SystemAnnotationDict(dict):
    """Transparent wrapper for _sysan so you can update it as
    if it were a dict and the changes get pushed to the sqlalchemy object

    """

    def __init__(self, source):
        self.source = source
        super(SystemAnnotationDict, self).__init__(source._sysan)

    def update(self, system_annotations={}):
        system_annotations = sanitize(system_annotations)
        temp = sanitize(self.source._sysan)
        temp.update(system_annotations)
        self.source._sysan = temp
        super(SystemAnnotationDict, self).update(system_annotations)

    def __setitem__(self, key, val):
        self.update({key: val})

    def __delitem__(self, key):
        del self.source._sysan[key]
        self.update()


class PropertiesDict(dict):
    """Transparent wrapper for _props so you can update it as
    if it were a dict and the changes get pushed to the sqlalchemy object

    """

    def __init__(self, source):
        self.source = source
        super(PropertiesDict, self).__init__(
            source.property_template(source._props))

    def update(self, properties={}):
        properties = sanitize(properties)
        temp = sanitize(self.source._props)
        temp.update(properties)
        self.source._props = temp
        super(PropertiesDict, self).update(temp)

    def __setitem__(self, key, val):
        self.update({key: val})

    def __delitem__(self, key):
        raise RuntimeError('You cannot delete ORM properties, only void them.')