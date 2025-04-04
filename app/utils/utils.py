

def get_field(instance, field_path):
    attr = instance
    for elem in field_path.split('.'):
        try:
            attr = getattr(attr, elem)
        except AttributeError:
            return None
    return attr
