import json

def champ_id_remap():
    original_champ_id = {}
    remapped_champ_id = {}

    with open('../id_to_key.json', 'r') as fp:
        original_champ_id = json.load(fp)

    for i, champ_name in enumerate(original_champ_id):
        remapped_champ_id[original_champ_id[champ_name]] = i
    
    return remapped_champ_id
