"""
Merge C22-23 table together so that they can be accessed in one place
"""

import csv
import os

def file_opener(f_name):
	data = []
	
	try:
		fl = open(f_name, 'r')
		f_csvread = csv.reader(fl, dialect = 'excel')
		# grab headers then grab data
		headers = next(f_csvread)
		for line in f_csvread:
			data.append(line)
		fl.close()

	except FileNotFoundError:
		print("{} not found!".format(f_name))
		headers = []
		
	return headers, data


# open and read in data from each sheet
# first for catalogue/APASS file
cat_head, cat_data = file_opener('C22-23_1.csv')
if not cat_data:
	print("File reading failed! Exiting...")
	quit()

# store obj data by name
obj_dict = {}
for line in cat_data:
	# include notes from cat file
	obj_dict[line[0]] = line[1:]
	
# grab obs data
obs_head, obs_data = file_opener('C22-23_2.csv')
if not obs_data:
	print("File reading failed! Exiting...")
	quit()

# now need to cross-match by name
for line in obs_data:
	try:
		# merge notes columns
		obj_dict[line[0]][-1] += ' ' + line[-1]
		obj_dict[line[0]] += line[1:-1]
	except KeyError:
		obj_dict[line[0]] = ['']*(len(cat_data[0])-2) + line[1:]
		
# WANT TO ADD CHECK BY COORDS WHEN CROSS-CYCLE

# output to new file
# second notes col removed as merged
out_head = ['Obj_name', 'Metal_flag'] + cat_head[2:] + obs_head[1:-1]
lenh =  len(out_head)
print("Outputting {} headers.".format(lenh))
out_data = []
for key in obj_dict:
	out_line = [key] + obj_dict[key]
	out_data.append(out_line)
	
# compare object names from each set
cat_names = []
for item in cat_data:
	cat_names.append(item[0])
obs_names = []
for item in obs_data:
	obs_names.append(item[0])
obs_names.sort()
cat_names.sort()

missing = []
for x, item in enumerate(cat_names):
	if item == obs_names[x-len(missing)]:
		pass
	else:
		missing.append(cat_names[x])
print("The following objects are missing from observation data:")
for it in missing:
	print(it)
	
	
out_name = 'C22-23-merged.csv'
with open(out_name, 'w') as outf:
	outwriter = csv.writer(outf)
	outwriter.writerow(out_head)
	outwriter.writerows(out_data)
	outf.close()
	
	
	
