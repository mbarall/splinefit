def get_options(args, delimiter="="):
    d_args = {}
    nonoptions = []
    for arg in args[1::]:
        try:
            key, value = arg.split(delimiter)
            d_args[key] = value
        except:
            nonoptions.append(arg)
    d_args['args'] = nonoptions

    return d_args

def check_options(args, options):
    args = get_options(args[1:])
    for arg in args:
        if "-" in arg:
            _arg = arg[1:]
        elif "args" in arg:
            continue
        else:
            _arg = arg

        if _arg not in options:
            raise ValueError("Unknown option: %s" %  _arg)

def print_options(options):
    for option in options:
        print(option, ":", options[option])
