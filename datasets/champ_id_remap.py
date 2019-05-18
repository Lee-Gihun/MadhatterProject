import json

def champ_id_remap():
    original_champ_id = {}
    remapped_champ_id = {}

    with open('../id_to_key.json', 'r') as fp:
        original_champ_id = json.load(fp)

    for i, champ_name in enumerate(original_champ_id):
        remapped_champ_id[original_champ_id[champ_name]] = i
    
    return remapped_champ_id

def get_original_champ_id(remapped_champ_id, champ_idx):
    for original_id, remapped_id in remapped_champ_id.iteritems():
        if remapped_id == champ_idx:
            return original_id
