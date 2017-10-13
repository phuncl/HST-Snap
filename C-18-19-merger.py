"""
Read Cycle 18/19 WD data and reformat to new standardised output \
"""

import csv
import os

HEADERS =  ['Obj_name', 'RA', 'DEC', 'HST-T_eff', 'errHST-T_eff', 'HST-logg', # 0-5
			'errHST-logg', 'HST-V_mag', 'errHST-V_mag', 'Mass_wd', 'errMass_wd', # 6-10
			'HST-Si/H', 'HST-errSi/H', 'HST-C/H', 'HST-errC/H'] # 11-14

# import csv file to memory and read data
data_block = []
with open('C18-19_1.csv', 'r') as file_in:
	file_reader = csv.reader(file_in, delimiter = ',')
	col_headers = next(file_reader)
	
	# write to variable and convert to float where possible
	for line in file_reader:
		writeline = []
		for item in line:
			try:
				writeline.append(float(item))
			except ValueError:
				writeline.append(str(item))		
		data_block.append(writeline)

# extract useful columns from data_block
# key cols (present in all files) needed are 
# Object_name, RA, DEC, T_eff, errT_eff, logg, errlogg, Vmag, errVmag
# optional cols are
# Mass, errMass, PM-RA, PM-DEC, Type, Si/H, errSi/H, C/H, errC/H
# then include column for notes
stripped_data = []
for line in data_block:
	print("Stripping data for {}.".format(line[0]))
	stripped_line = [str(line[0])]
	comb_coords = line[1]
	# split RA and DEC
	stripped_line.append(str(comb_coords[:4]))
	stripped_line.append(str((comb_coords[4:])))
	# create data line for output	
	for i in range(2, 10):
		stripped_line.append(str(line[i]))
	for i in range(16, 20):
		stripped_line.append(line[i])
	
	stripped_data.append(stripped_line)
	
# output data to compilation table file
print("Writing stripped data to new file.")
with open("C18-19-merged.csv", 'w') as f_out:
	header_writer = csv.writer(f_out, delimiter = ',')
	header_writer.writerow(HEADERS)
	header_writer.writerows(stripped_data)
print("Data streaming completed.")


