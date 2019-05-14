from pathlib import Path
import re
from django.conf import settings
from django.shortcuts import render


def path_competition_data():
	base_dir = Path(settings.BASE_DIR)
	config_file	= base_dir	/ 'config.txt'
	if config_file.exists():
			data_settings = config_file.read_text()
			if not re.search(r'default_path_of_competition_data:\s*True\b', data_settings):

				similarities = re.search(r'relative_path:\s*\"(([\w\d]+[\\\/]?)*)\"', data_settings)
				if similarities:
					
					relative_path = similarities.group(1)
					path = base_dir / relative_path	

					return path
	return base_dir / 'competition_data'

def read_start_list():
	data_path = path_competition_data()
	start_protocol_files = list(data_path.glob('*.evt')) #User can contain several start protocol files but we will read only the first 
	if not start_protocol_files:
		return	0 
	else:
	    start_f = data_path / start_protocol_files[0]
	    return(start_f.read_text(encoding='utf16'))


def compose_comp_data(events):

	events.sort(key=lambda tup: (int(tup[0]), int(tup[1]), int(tup[2])))
	
	competitions = []
	names_of_competitions = []
	competition = []
	k = int(events[0][0])
	for i in range(len(events)):
		if (int(events[i][0]) == k):
			competition.append(tuple(events[i][:3])) 
		else:
			competitions.append(list(competition))
			names_of_competitions.append(events[i - 1][3]) 
			competition.clear()
			
			competition.append(tuple(events[i][:3]))
			k += 1

	competitions.append(list(competition))
	names_of_competitions.append(events[len(events) - 1][3])

	comps_with_names = zip(names_of_competitions, competitions)

	return comps_with_names