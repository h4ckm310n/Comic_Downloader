import json


def get_max_process():
    with open('config.json', 'r') as json_file:
        process_max = json.load(json_file)['process_number']
    return process_max


dl_state_dict = {
                    'waiting': -1,
                    'analyzing': 0,
                    'downloading': 1,
                    'finished': 2,
                    'pause': -2
                }
