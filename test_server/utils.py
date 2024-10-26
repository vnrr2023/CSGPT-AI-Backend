import re

json_error=[
    "Oops! I wasn't able to process the request. Please try again.",
    "Apologies, I couldn't complete your request. Kindly try once more.",
    "Sorry about that! Something went wrong. Please give it another shot.",
    "I wasn't able to handle your request. Please try again in a moment.",
    "Unfortunately, I couldn't process the request this time. Please try again later.",
    "Oops! There was a problem processing your request. Try again when you're ready.",
    "My apologies! I couldn't complete your request. Please try again shortly.",
    "It looks like I wasn't able to process that. Please give it another try.",
    "Sorry! There was an issue processing your request. Please try again soon.",
    "I couldn't process the request this time. Please try again in a bit!"
]

cs_error=[
    "Oops! Sorry, I don't have any information about it. Please ask a relevant question related to Computer Science.",
    "Apologies, I don't have details on that topic. Please ask a Computer Science-related question.",
    "Sorry! I don't have information on that. Could you ask something related to Computer Science?",
    "Unfortunately, I don't have any knowledge on that. Please try asking a question about Computer Science.",
    "Oops! I'm unable to provide information on that. Please ask a question related to Computer Science.",
    "My apologies, I don't have data on this. Could you ask something relevant to Computer Science?",
    "Sorry! I don't have any information about that. Please ask a question in the field of Computer Science.",
    "I don't have information on this topic. Please try asking a Computer Science-related question.",
    "Oops! It looks like I don't have details on that. Please ask a question related to Computer Science.",
    "Sorry, I don't have any knowledge about that. Please ask a Computer Science-related question instead."
]

program_error=[
    "Oops! Sorry, I don't have the ability to program. I will enhance myself in the near future.",
    "Apologies, but I lack programming capabilities. I plan to improve in the future.",
    "Sorry! I don't have the ability to code right now. I hope to enhance my skills soon.",
    "Unfortunately, I can't program at the moment. I'm working on improving myself in the near future.",
    "Oops! I don't have programming abilities currently. I aim to enhance my skills soon.",
    "My apologies, but I can't code right now. I will strive to develop this capability soon.",
    "Sorry! I lack the ability to program. I plan to work on this in the future.",
    "I currently don't have programming abilities. I hope to improve in the near future.",
    "Oops! It seems I can't program at this time. I will work on enhancing myself soon.",
    "Sorry, I don't have programming skills at the moment. I will aim to improve in the future."
]



def fix_json_string_with_re(input_str):
    input_str = re.sub(r'[‘’]', "'", input_str)
    input_str = re.sub(r'[“”]', "'", input_str)
    input_str = re.sub(r'\n', r'\\n', input_str)
    input_str = re.sub('\*', '*', input_str)
    return input_str