def update_locals(module_dict, l):
    l.update(dict([(key, module_dict[key]) for key in module_dict
                   if not key.startswith('_')]))
