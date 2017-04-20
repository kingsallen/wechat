# coding:UTF-8

def get_module_name(o):
    module_full_name = o.__module__
    module_name = module_full_name.split('.')[-1]
    if not module_name:
        raise Exception("Fatal Error: wrong module name")
    return module_name
