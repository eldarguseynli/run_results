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
	if content[0].isdigit(): events.append(re.match(r'(\d+),([^,]+),([^,]+),([^,]*)', content).groups()) #control case when data begins from the begining of file
	events.extend(re.findall(r'\n(\d+),([^,]+),([^,]+),([^,]*)', content)) #extract information about every heat (event n, round n, heat n, name)
	if not events: return render(request, 'nonexistent_file.html', {'path' : str(utils.path_competition_data())})

	return render(request, 'start_list.html', {'comps_with_names': utils.compose_comp_data(events)})

def start_protocol(request, number, round, heat):
	
	content = utils.read_start_list()

	if not content: return render(request, 'nonexistent_file.html', {'path' : str(utils.path_competition_data())})	
	else:
		rx = number + ',' + round + ',' + heat + ',' + r'.*(((.|\n)(?!\n\d))*,?)' #regex for search of block of data about participant of certain heat
		if content[0].isdigit(): simularities =  re.search(rx, content) 
		else: simularities = re.search('\n' + rx, content) #change regex if data begins from the begining of file  
		if not simularities: return render(request, 'nonexistent_start_protocol.html',
									 	  {'path' : str(utils.path_competition_data()), 'number': number, 'round': round, 'heat': heat })
		participants = re.findall(r'\n[,	 ](\d+),(\d+),([^,]*),([^,]*),([^,]*),', simularities.group(1)) #extract different types of information for every person
		competition_code = re.search(r'\d+,([^,]+),([^,]+),([^,]*)', simularities.group(0)).groups()

		participants = [(tup[0], tup[1], tup[2] + ' ' + tup[3], tup[4]) for tup in participants] #concatenate first and second names
		return render(request, 'start_protocol.html', {'participants': participants, 'competition_code' : competition_code} )
	

def result_list(request):

	data_path = utils.path_competition_data()

	events = []

	lif_files = list(data_path.glob('*.lif'))

	if not lif_files: return render(request, 'no_lifs_files.html', {'path' : data_path})
	for f_name in lif_files:
		with open(f_name.absolute(), encoding='utf16') as f:
			events.append(re.search(r'(\d+),([^,]+),([^,]+),([^,]+)', f.readline()).groups()) #read and parse the first line in all "lif" file

	return render(request, 'result_list.html', {'comps_with_names': utils.compose_comp_data(events)})

def result_protocol(request, number, round, heat):

	data_path = utils.path_competition_data()
	for f_name in data_path.glob('*.lif'):
		with open(f_name.absolute(), encoding='utf16') as f:
			competition_code = re.search(r'^([^,]+),([^,]+),([^,]+),([^,]+)', f.readline()).groups() #read and parse the first line in "lif" file
			if (competition_code[0] == number) & (competition_code[1] == round) & (competition_code[2] == heat): #find file with information about certain heat 
				content = f.read()
				participants = []
				participants.append(re.match(r'([^,]*),([^,]*),[^,]*,([^,]*),([^,]*),([^,]*),([^,]*)', content).groups())
				participants.extend(re.findall(r'\n([^,]*),([^,]*),[^,]*,([^,]*),([^,]*),([^,]*),([^,]*)', content)) #parse information about participants
				
				participants = [(tup[0], tup[1], tup[2] + ' ' + tup[3], tup[4], tup[5]) for tup in participants] #concatenate first and second names
				return render(request, 'result_protocol.html',
							 {'participants': participants, 'competition_code' : competition_code[1:4]} )
	return render(request, 'nonexistent_result_protocol.html',
				 {'path' : str(utils.path_competition_data()), 'number': number, 'round': round, 'heat': heat })

def round_results(request, number, round):

	data_path = utils.path_competition_data()
	lif_files = list(data_path.glob('*.lif'))
	last_lif = len(lif_files) - 1

	if last_lif < 0:
		return render(request, 'no_round_information.html',
					 {'path' : str(utils.path_competition_data()), 'number': number, 'round': round})

	competition_code = tuple()
	real_participants = []
	fs_participants = []
	nt_participants = []
	na_participants = []

	for index, f_name in enumerate(lif_files):
		with open(f_name.absolute(), encoding='utf16') as f:

			if index == last_lif:
				competition_code = re.match(r'^([^,]+),([^,]+),[^,]+,([^,]+)', f.readline()).groups()
			else:
				competition_code = re.match(r'^([^,]+),([^,]+)', f.readline()).groups()

			if (competition_code[0] == number) & (competition_code[1] == round):

				content = f.readlines()[0:]

				for line in content:

					simularities = (re.match(r'\d+,[^,]*,[^,]*,([^,]*),([^,]*),([^,]*),([^,]*)', line))
					if simularities:
						real_participants.append(simularities.groups())
					else:
						simularities = (re.match(r'(ФС),[^,]*,[^,]*,([^,]*),([^,]*),([^,]*),([^,]*)', line))
						if simularities:
							fs_participants.append(simularities.groups())
						else:
							simularities = (re.match(r'(НС),[^,]*,[^,]*,([^,]*),([^,]*),([^,]*),([^,]*)', line))
							if simularities:
								nt_participants.append(simularities.groups())
							else:
								simularities = (re.match(r'(НФ),[^,]*,[^,]*,([^,]*),([^,]*),([^,]*),([^,]*)', line))
								if simularities:
									na_participants.append(simularities.groups())

					
	real_participants = [(tup[0] + ' ' + tup[1], tup[2], tup[3]) for tup in real_participants]
	fs_participants = [(tup[1] + ' ' + tup[2], tup[3]) for tup in fs_participants]
	nt_participants = [(tup[1] + ' ' + tup[2], tup[3]) for tup in nt_participants]
	na_participants = [(tup[1] + ' ' + tup[2], tup[3]) for tup in na_participants]

	if real_participants:
		
		real_participants.sort(key=lambda tup: tup[2])

		participant_with_common_place = []
		ordered_real_participants = []

		participant_with_common_place.append(real_participants[0])
		result = real_participants[0][2]
		
		for participant in real_participants[0:]:
			participant_result = participant[2]
			
			if participant_result == result:
				participant_with_common_place.append(participant)
				
			else:
				
				ordered_real_participants.append(list(participant_with_common_place))
				participant_with_common_place.clear()
				participant_with_common_place.append(participant)
				result = participant_result
		ordered_real_participants.append(list(participant_with_common_place))
	
			
	context = {'ordered_real_participants': ordered_real_participants, 'fs_participants': fs_participants, 'nt_participants': nt_participants,
			'na_participants': na_participants, 'competition_name': competition_code[2], 'round': round }

	return render(request, 'round_result_protocol.html', context)

