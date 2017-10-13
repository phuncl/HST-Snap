"""
Generalised version of reformat program
designed to  work for all snapshot tables.
All data sorted into dictionary (by name)
so could still have double stars -
need to check by COORDS eventually.
"""

import csv
import os

def file_opener(f_name):
	"""
	Formulaic open and close of file, extracting headers and data
	"""
	data = []
	try:
		fl = open(f_name, 'r')
		f_csvread = csv.reader(fl, dialect = 'excel')
		headers = next(f_csvread)
		for line in f_csvread:
			data.append(line)
		fl.close()
	except FileNotFoundError:
		print("{} not found!".format(f_name))
		new_name = input('Please provide a correct filename: ')
		file_opener(f_name)
		
	return headers, data

def header_finder(master, padowan):
	"""
	Scan a list of file headers against the master headers,
	return a list of required indexes
	"""
	traits_indices = {}
	for trait in padowan:
		if trait in master:
			traits_indices[trait] = padowan.index(trait)

	return traits_indices
			

#  MAIN  ###############################################################

# read all output column headers from file
with open('HST-snapshot-cols.csv', 'r') as fin:
	fread = csv.reader(fin, delimiter=',')
	master_headers = next(fread)

# read in data for (C18, C22, targets) files
# put headers into list, data into lists of lists
targets_headers, targets_data = file_opener('targets.csv')
c18_headers, c18_data = file_opener('C18-19-merged.csv')
c22_headers, c22_data = file_opener('C22-23-merged.csv')
datasets = [targets_data, c18_data, c22_data]

# determine useful cols for each set of headers
c18_indices = header_finder(master_headers, c18_headers)
c22_indices = header_finder(master_headers, c22_headers)
targets_indices = header_finder(master_headers, targets_headers)

data_lookup = {'c18':[c18_indices,c18_headers,c18_data],
				'c22':[c22_indices,c22_headers,c22_data],
				'targets':[targets_indices,targets_headers,targets_data]}

# initialise data dictionary and each key within it
obj_dict = {}
synonyms = {}
for line in c18_data:
	obj_dict[line[0]] = []
for line in c22_data:
	obj_dict[line[0]] = []
for line in targets_data:
	# if alt name is present, replace with WD name
	# also create synonym pair tuple
	if obj_dict.pop(line[1], -1) != -1:
		# if synonym has been found
		print("Synonym found between catalogues for {0} and {1}.".format(line[0], line[1]))
		synonyms[line[0]] = line[1]
	# create new key either way
	obj_dict[line[0]] = []
# all keys created

# pull data on a by-header basis
# check if multpiple data available
# and resolve which to use - BY USER CHOICE

for header in master_headers:
	print('\n' + header)
	for obj_name in obj_dict:
		# initialise all catalogue vals to false
		data_pts = {'c18':False,'c22':False, 'targets':False}
		num_data = 0
		dat_output = ""
		for dset in data_lookup:
			#check if catalogue has the header
			if header in data_lookup[dset][1]:
				# scan catalogue to find correct obj list
				for line in data_lookup[dset][2]:
					if line[0] == obj_name:
						try:
							data_pts[dset] = line[data_lookup[dset][0][header]]
							num_data += 1
						except KeyError:
							pass
						break
		#~ if num_data:
			#~ print(data_pts)
			#~ print("{0} value(s) for {1} in object {2}\n".format(num_data, header, obj_name))
		# if single value, use as output
		if num_data == 1:
			for pt in data_pts:
				if data_pts[pt]:
					dat_output = data_pts[pt]
		# if multiple values, allow user to choose value
		elif num_data > 1:
			print("\nMultiple values found for {0} of object {1}:".format(header, obj_name))
			# include each unique value
			multi_pts = []
			for pt in data_pts:
				if data_pts[pt]:
					if data_pts[pt] not in multi_pts:
						#~ try:
							#~ multi_pts.append(float(data_pts[pt]))
						#~ except:
						multi_pts.append(data_pts[pt])
						print(pt, data_pts[pt])
			# if only 1 unique value, skip selection
			if len(multi_pts) == 1:
				dat_output = multi_pts[0]
				print("Only one unique value found ({})".format(dat_output))
			while not dat_output:
				if not multi_pts:
					dat_output = ""
					break
				pick = str(input("Give catalogue name (eg c18) of the data point to be used: "))
				try:
					dat_output = data_pts[pick]
				except KeyError:
					print("Incorrect catalogue name given.")
		# if no value, use blank as output
		else:
			dat_output = ""
		# append the data point to that line
		obj_dict[obj_name].append(dat_output)
	print("\n{} data collected.".format(header))

# output content of data dictinary to file
output_listing = [master_headers]
for obj in obj_dict:
	output_listing.append(obj_dict[obj])

f_compiled = open('HST_compiled_data.csv', 'w')
f_writer = csv.writer(f_compiled, delimiter=',')
f_writer.writerows(output_listing)
f_compiled.close()
print("Data written to file. Exiting...")
