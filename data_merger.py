"""
General program to read in master table,
read in a donor table,
and add data to appropriate cols of HST
"""

import csv
import glob


def get_donorfile():
	# list all <something> separated variable files in dir, and pick one
	flist = glob.glob('*sv')
	for i,nam in enumerate(flist):
		print("{}\t{}".format(i,nam))

	fn = ""
	while not fn:
		try:
			fn = flist[int(input("Give index of desired file: "))]
		except IndexError:
			print("Invalid index given!")
	return fn


def master_data_reader():
	# read in HST combined data to memory
	with open("HST_compiled_data.csv", 'r') as fin:
		frd = csv.reader(fin, delimiter = ',')
		heads = next(frd)
		dats = list(frd)

	return heads, dats


def generic_reader(fn):
	# for a given file, open and print one line
	# ask for delimiter characters
	# get headers and data
	print("\nOpening {}".format(fname))
	print("First line of file reads:")
	with open(fn, 'r') as fin:
		print(fin.readline())
	
	delim = input("What is the delimiter used in this file?\n")
	print()
	
	with open(fn, 'r') as fin:
		frd = csv.reader(fin, delimiter = delim)
		heads = next(frd)
		dats = list(frd)
		# strip leading/trailing whitespace for all lines
		dats = [[x.strip() for x in y] for y in dats]

	return heads, dats


def head_lookup(donor_h, main_h):
	# create lookup dictionary for inputted headers
	h_dict = {}
	for h in donor_h:
		resp = ""
		while not resp:
			resp = input("Would you like to use new {} values in overwrite? (y/n) ".format(h)).lower()
			if resp == "y":
				try:
					h_dict[h] = main_h.index(h)
					print("{} cross-indexed.\n".format(h))
				except:
					print("Header <{}> not found in HST file.".format(h))
					print("Skipping {} values.\n".format(h))
			elif resp == "n":
				print("Skipping {} values.\n".format(h))
			else:
				resp = ""
				print("Invalid response.")
	
	return h_dict


def star_listing(donor_dat, mst_dat):
	# Create dict of star:new-line-index
	# for all donor file stars in hst data
	mst_names = [x[0] for x in mst_dat]
	donor_names = [y[0] for y in donor_dat]
		
	name_dict = {}
	for s in mst_names:
		if s in donor_names:
			name_dict[s] = donor_names.index(s)
	
	return name_dict


def error_watcher(val_name):
	# When a value overwritten take name of value
	# if it was not an error then add its corresponding error to watchlist
	if val_name[:3] == "err":
		return "Already-an-error"
	else:
		return "err" + val_name


def pointone_test(x, y, proximity = 0.1):
	# check if values are within +- 0.1
	try:
		x = float(x)
		y = float(y)
	except TypeError:
		return False
	
	if abs(x-y) <= proximity:
		return True
	else:
		return False


def save_master_csvfile(headers, data_lists, mst_name):
	# write headers and data to master file
	with open(mst_name, 'w') as fout:
		fwrt = csv.writer(fout, delimiter = ',')
		fwrt.writerow(headers)
		fwrt.writerows(data_lists)
	print("Data saved to {}!".format(mst_name))


def get_filename():
	# Get savename from user
	# check only 1 extension given
	fnm = ""
	while not fnm:
		fnm = input("Give name for save file (no extension):\n") + '.csv'
	
	return fnm


############################  MAIN  ####################################
# get donor file
fname = get_donorfile()

# define new headers and new data
donor_heads, donor_data = generic_reader(fname)
master_heads, master_data =  master_data_reader()

# obtain cross reference dictionary for headers and for stars
# do not pass Obj_name as that is reference point
cross_ref = head_lookup(donor_heads[1:], master_heads)
star_ref = star_listing(donor_data, master_data)

# get desired file savename
out_name = get_filename()
print("Data will be saved upon program completion.")

# update data in master file
# get user input for conflicting data
for a, line in enumerate(master_data):
	if line[0] in star_ref:
		# want to automatically take donor error if donor val taken
		# make list of error names to automatically add (per object)
		errwatch = []
		print("\nExamining data for {}.".format(line[0]))
		for h in cross_ref:
			# get new value from new_data
			donor_val = donor_data[star_ref[line[0]]][donor_heads.index(h)]
			prev_val = line[cross_ref[h]]
						
			# check if an err for added val, and add
			if h in errwatch:
				master_data[a][cross_ref[h]] = donor_val
				print("{0} automatically written for {1}".format(h, line[0]))
			
			# skip iteration if no donor value
			elif donor_val == "":
				continue
			
			# skip iteration, update errwatch if donor values are same
			elif prev_val == donor_val:
				print("Values are identical.")
				# add to watchlist
				errwatch.append(error_watcher(h))

			# if donor value, and no value in master, write into data
			elif prev_val == "":
				master_data[a][cross_ref[h]] = donor_val
				print("New {0} value written for {1}".format(h, line[0]))
				# add to watchlist
				errwatch.append(error_watcher(h))
			
			# if values within 0.1, take new value
			elif pointone_test(donor_val, prev_val):
				master_data[a][cross_ref[h]] = donor_val
				print("New {0} value written for {1}".format(h, line[0]))
				print("Values were within 0.1 of each other.")
				# add to watchlist
				errwatch.append(error_watcher(h))

			# should print only if two non-null, non-similar unique values
			else:
				print("{}:".format(h))
				print("New value = {}".format(donor_val))
				print("Previous value = {}".format(prev_val)) 
				# ask user for decision
				overwriting = ""
				while overwriting not in ("y","n"):
					overwriting = input("Do you want to overwrite stored value with new value? (y/n) ")
					if overwriting == "y":
						master_data[a][cross_ref[h]] = donor_val
						# add to watchlist
						errwatch.append(error_watcher(h))
					elif overwriting == "n":
						pass
					else:
						print("Try again, numbskull...")
print("""\n
************************\n
All data points updated.\n
************************\n
""")

# Write master data to file
save_master_csvfile(master_heads, master_data, out_name)
print("Data saved! Exiting...")

