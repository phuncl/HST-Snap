"""
Parse C25 file and extract T_eff and log(g) from notes,
then append columns to table and resave
"""

# import csv file to memory and read data
data_block = []
with open('C18-19_1.csv', 'r') as file_in:
	file_reader = csv.reader(file_in, delimiter = ',')
	col_headers = next(file_reader)
	
	# write to variable and convert to float where possible
	for line in file_reader:
		print(line)
		writeline = []
		for item in line:
			try:
				writeline.append(float(item))
			except ValueError:
				writeline.append(str(item))		
		data_block.append(writeline)

for line in data_block:
	notes = line[-1].split(',')
	temp = notes[1].split(' ')[1]
	
