def set_attrs(obj, **kwargs):
    """Set many attrs to an object."""
    for k, v in kwargs.items():
        setattr(obj, k, v)
