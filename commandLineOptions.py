def add(parser):
    parser.add_argument('-L', '--coppeliasim-library', type=str, required=True, help='Path to the coppeliaSim shared library')
    parser.add_argument('-c', '--startup-script-string', type=str)
    parser.add_argument('-v', '--verbosity', type=str)
    parser.add_argument('-w', '--statusbar-verbosity', type=str)
    parser.add_argument('-x', '--dlg-verbosity', type=str)
    parser.add_argument('-a', '--additional-addon-script-1', type=str)
    parser.add_argument('-b', '--additional-addon-script-2', type=str)
    parser.add_argument('-g', '--app-arg', action='append', type=str)
    parser.add_argument('-G', '--named-param', action='append', type=str)
    parser.add_argument('-H', '--headless', action='store_true')

def parse(args):
    from ctypes import c_char_p
    from coppeliaSimLib import simSetStringParam, simSetNamedStringParam

    if args.startup_script_string:
        sim_stringparam_startupscriptstring = 125
        s = c_char_p(args.startup_script_string.encode('utf-8'))
        simSetStringParam(sim_stringparam_startupscriptstring, s)

    if args.verbosity:
        sim_stringparam_verbosity = 121
        s = c_char_p(args.verbosity.encode('utf-8'))
        simSetStringParam(sim_stringparam_verbosity, s)

    if args.statusbar_verbosity:
        sim_stringparam_statusbarverbosity = 122
        s = c_char_p(args.verbosity.encode('utf-8'))
        simSetStringParam(sim_stringparam_statusbarverbosity, s)

    if args.dlg_verbosity:
        sim_stringparam_dlgverbosity = 123
        s = c_char_p(args.verbosity.encode('utf-8'))
        simSetStringParam(sim_stringparam_dlgverbosity, s)

    if args.additional_addon_script_1:
        sim_stringparam_additional_addonscript1 = 11
        s = c_char_p(args.verbosity.encode('utf-8'))
        simSetStringParam(sim_stringparam_additional_addonscript1, s)

    if args.additional_addon_script_1:
        sim_stringparam_additional_addonscript2 = 12
        s = c_char_p(args.verbosity.encode('utf-8'))
        simSetStringParam(sim_stringparam_additional_addonscript2, s)

    if args.app_arg:
        for i, arg in enumerate(args.app_arg):
            sim_stringparam_app_arg1 = 2
            s = c_char_p(arg.encode('utf-8'))
            simSetStringParam(sim_stringparam_app_arg1 + i, s)

    if args.named_param:
        for i, arg in enumerate(args.named_param):
            k, v = arg.split('=', 1)
            k = c_char_p(k.encode('utf-8'))
            n = len(v)
            v = c_char_p(v.encode('utf-8'))
            simSetNamedStringParam(k, v, n)

    sim_gui_all = 0x0ffff
    sim_gui_headless = 0x10000
    if args.headless:
        options = sim_gui_headless
    else:
        options = sim_gui_all
    return options
