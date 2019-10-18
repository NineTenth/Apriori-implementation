"""
this is the main entrance for Association Analysis part of project 1

tested with python 3.X
"""

import re
import pickle

rules = [] # it is usually, if not always, a bad idea to use global variables.
           # used here to reduce the number of parameters passed around


def _get_part_num(part):
    part_num = 0 # in order not to break the program, 0 will be returned instead -1
    if part.upper() == "RULE":
        part_num = 0
    elif part.upper() == "BODY":
        part_num = 1
    elif part.upper() == "HEAD":
        part_num = 2
    else:
        print("wrong input")

    return part_num


def parse_template_1_command(command):
    """
    parse command for template 1

    return:
        _part: rule, body, or head
        _count: "any", "number (integer)", or "none"
        _genes: list of gene elements
    """
    command = command.replace('"', '')
    command = command.replace('\'', '')
    command = command.replace('[', '')
    command = command.replace(']', '')
    command = command.replace(' ', '')

    segments = re.split(',', command.upper())
    _part = segments[0]
    _count = segments[1]
    _genes = segments[2:]

    return _part, _count, _genes


def filter_any_none(part, mode, genes):
    filtered_rules = []
    for item in rules:
        for gene in genes:
            if gene in item[part]:
                filtered_rules.append(item)
                break
    if mode == "NONE":
        filtered_rules = [item for item in rules if item not in filtered_rules]
    return filtered_rules


def filter_by_number(part, count, genes):
    """
    get the rules/body/head which contains exactly count number Gs out of genes

    parameters:
        part:
        count:
        genes:

    returns:
    """
    filtered_rules = []
    for item in rules:
        counting = 0
        for gene in genes:
            if gene in item[part]:
                counting += 1
        if count == counting:
            filtered_rules.append(item)

    return filtered_rules


def run_template_1(command):
    """
    the format of command is like
        "'rule/body/head','any/number/none',['G59_UP','G10_Down']"
    """
    part, count, genes = parse_template_1_command(command)

    filtered_rules = []
    part_num = _get_part_num(part)   # which part of the saved result to loop on
    if count == "ANY" or count == "NONE":
        filtered_rules = filter_any_none(part_num, count, genes)
    else:
        filtered_rules = filter_by_number(part_num, int(count), genes)

    return filtered_rules


def parse_template_2_command(command):
    segments = re.split(',', command.strip())
    _part = segments[0].strip()[1:-1]  # pay attention to the quotes
    _num = int(segments[1])
    return _part, _num


def run_template_2(command):
    """
    the format of command is like:
        "'RULE',2"
    """
    part, number = parse_template_2_command(command)

    filtered_rules = []
    part_num = _get_part_num(part)

    for item in rules:
        if len(item[part_num]) >= number:
            filtered_rules.append(item)

    return filtered_rules


def parse_template_3_command(command):
    """
    example:
        "'1or1','body','any',['g10_down'],'head',1,['g59_up']"
    """
    segments = re.split(',', command)
    part_one = segments[0][1]
    part_two = segments[0][-2]
    relation = "and" if len(segments[0]) == 7 else "or"

    first_comma = command.find(',')
    divide_comma = 0 # the position of comma that seperates the first and second command
    if part_one == "1":
        divide_comma = command.find(']') + 1
    else:
        divide_comma = [m.start() for m in re.finditer(r',', command)][2]

    part_one_command = command[first_comma + 1 : divide_comma]
    part_two_command = command[divide_comma + 1 :]

    return part_one, relation, part_two, part_one_command, part_two_command


def run_template_3(command):
    """
    the command format is like:
        "'1and2',command of template 1,command of template 2"
    """
    part_one, relation, part_two, part_one_command, part_two_command = parse_template_3_command(command)

    filtered_rules_one = []
    if part_one == "1":
        filtered_rules_one = run_template_1(part_one_command)
    else:
        filtered_rules_one = run_template_2(part_one_command)

    filtered_rules_two = []
    if part_two == "1":
        filtered_rules_two = run_template_1(part_two_command)
    else:
        filtered_rules_two = run_template_2(part_two_command)

    filtered_rules = []
    if relation == "and":
        # intersection two sets
        filtered_rules = [item for item in filtered_rules_one if item in filtered_rules_two]
    else:
        # union two sets
        filtered_rules = filtered_rules_one
        filtered_rules.extend(item for item in filtered_rules_two if item not in filtered_rules_one)

    return filtered_rules


def parse_user_input_and_run(content):
    open_parenthesis = content.find("(")   # not work in Python 2.x
    close_parenthesis = content.find(")")
    if open_parenthesis == -1 or close_parenthesis == -1:
        print("wrong command entered.")
        return
    _content = content[open_parenthesis + 1 : close_parenthesis]
    template_num = content[:open_parenthesis].upper()

    filtered_rules = []
    if template_num == "TEMPLATE1":
        filtered_rules = run_template_1(_content)
    elif template_num == "TEMPLATE2":
        filtered_rules = run_template_2(_content)
    elif template_num == "TEMPLATE3":
        filtered_rules = run_template_3(_content)
    else:
        print("wrong command entered.")
        return

    for item in filtered_rules:
        print("%s -> %s" % (item[1], item[2]))
    print(len(filtered_rules))


def loop():
    user_input = ""
    while user_input != "q":
        user_input = input("please enter the command ('q' to end): ")
        if not user_input or user_input == "q":
            continue
        # user_input = "template3('1or1','body','any',['g10_down'],'head',1,['g59_up'])" # for easily testing result 31
        parse_user_input_and_run(user_input)


if __name__ == "__main__":
    with open("rules", "rb") as f:
        rules = pickle.load(f)
    loop()
