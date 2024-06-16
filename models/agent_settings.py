from agent_prompt import template_prompt_all

FILTER_ALL = {"operand": "$not", "list": ['0']}
FILTER_GENERAL = {"operand": "$not", "list": ['1', '2', '3', '4', '5', '6', '7', '8', '12', '14', '16', '17',
                                              '18', '19', '20', '21', '22', '23', '24', '25', '88', '89', '90', '91', '92', '93', '94', '95', '96', '97']}
FILTER_OBJECTION = {"operand": "$any", "list": [
    '88', '89', '90', '91', '92', '93', '94']}
FILTER_HR = {"operand": "$any", "list": [
    '17', '18', '19', '20', '21', '22', '23', '24']}
FILTER_NEED = {"operand": "$any", "list": ['95', '96', '97']}
FILTER_HISTORY_UAI = {"operand": "$any", "list": [
    '1', '2', '3', '4', '5', '6', '7', '8']}
FILTER_BASIC_COURSE = {"operand": "$any", "list": ['12', '16']}
FILTER_ADD_COURSE = {"operand": "$any", "list": ['14']}
FILTER_ADD_PACKAGE = {"operand": "$any", "list": ['85', '86', '87']}
FILTER_INTRNSHIPS = {"operand": "$any", "list": ['25']}
FILTER_FEES_COURSE = {"operand": "$any", "list": [
    '29', '30', '31', '32', '33', '34', '35']}


agent_settings = {
    'agent_all': {
        'template_prompt': template_prompt_all,
        'filter_data': FILTER_ALL,
        'filter_chunk': []
    },
}
