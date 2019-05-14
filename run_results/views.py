import re
from django.conf import settings
from . import utils 
import glob

from django.shortcuts import render



def index(request):
	return render(request, 'index.html')

def start_list(request):
	
	content = utils.read_start_list()
	if not content: return render(request, 'nonexistent_file.html', {'path' : str(utils.path_competition_data())})
	
	events = []
	if content[0].isdigit(): events.append(re.match(r'(\d+),([^,]+),([^,]+),([^,]*)', content).groups())
	events.extend(re.findall(r'\n(\d+),([^,]+),([^,]+),([^,]*)', content))
	if not events: return render(request, 'nonexistent_file.html', {'path' : str(utils.path_competition_data())})

	return render(request, 'start_list.html', {'comps_with_names': utils.compose_comp_data(events)})

def start_protocol(request, number, round, heat):
	
	content = utils.read_start_list()

	if not content: return render(request, 'nonexistent_file.html', {'path' : str(utils.path_competition_data())})	
	else:
		rx = number + ',' + round + ',' + heat + ',' + r'.*(((.|\n)(?!\n\d))*,?)'
		if content[0].isdigit(): simularities =  re.search(rx, content)
		else: simularities = re.search('\n' + rx, content)
		if not simularities: return render(request, 'nonexistent_protocol.html', {'path' : str(utils.path_competition_data()), 'number': number, 'round': round, 'heat': heat })
		participant = re.findall(r'\n[,	 ](\d+),(\d+),([^,]*),([^,]*),([^,]*),', simularities.group(1))
		competition_code = re.search(r'\d+,([^,]+),([^,]+),([^,]*)', simularities.group(0)).groups()

		participant = [(tup[0], tup[1], tup[2] + ' ' + tup[3], tup[4]) for tup in participant]
		return render(request, 'start_protocol.html', {'participants': participant, 'competition_code' : competition_code} )
	

def result_list(request):

	data_path = utils.path_competition_data()

	events = []

	lif_files = list(data_path.glob('*.lif'))

	if not lif_files: return render(request, 'no_lifs_files.html', {'path' : data_path})
	for f_name in lif_files:
		with open(f_name.absolute(), encoding='utf16') as f:
			events.append(re.search(r'(\d+),([^,]+),([^,]+),([^,]+)', f.readline()).groups())

	return render(request, 'result_list.html', {'comps_with_names': utils.compose_comp_data(events)})

def result_protocol(request, number, round, heat):

	data_path = utils.path_competition_data()
	for f_name in data_path.glob('*.lif'):
		with open(f_name.absolute(), encoding='utf16') as f:
			competition_code = re.search(r'(\d+),([^,]+),([^,]+),([^,]+)', f.readline()).groups()
			if (competition_code[0] == number) & (competition_code[1] == round) & (competition_code[2] == heat):
				content = re.search(r'\n(\n|.)*',f.read()).group(0)
				participants = re.findall(r'\n(\d+),([^,]*),[^,]*,([^,]*),([^,]*),([^,]*),([^,]*)', content)
				
				participants = [(tup[0], tup[1], tup[2] + ' ' + tup[3], tup[4], tup[5]) for tup in participants]
				print(participants)
				return render(request, 'result_protocol.html', {'participants': participants, 'competition_code' : competition_code[1:4]} )



