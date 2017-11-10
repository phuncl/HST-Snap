"""
General program to read in master table,
read in a donor table,
and add data to appropriate cols of HST
"""

import csv
import glob


def get_filelist():
	"""
	list all <something> separated variable files in dir, and pick one
	"""
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


def master_reader():
	"""
	read in master csv data file to memory
	"""
	print("\n\nChoose MASTER data file to update.")
	filnam = get_filelist()
	with open(filnam, 'r') as fin:
		frd = csv.reader(fin, delimiter = ',')
		heads = next(frd)
		dats = list(frd)

	return heads, dats


def generic_reader(fn):
	"""
	for a given file, open and print one line
	ask for delimiter characters
	get headers and data
	"""
	print("\nOpening {}".format(fn))
	print("First line of file reads:")
	with open(fn, 'r') as fin:
		print(fin.readline())
	
	delim = input("What is the delimiter used in this file?\n")
	print()
	
	with open(fn, 'r') as fin:
		frd = csv.reader(fin, delimiter = delim)
		hds = next(frd)
		dts = list(frd)
		# strip leading/trailing whitespace for all lines
		dts = [[x.strip() for x in y] for y in dts]

	return hds, dts
	

def donor_reader():
	"""
	read in donor data file tp memory
	"""
	print("\nChoose DONOR data file to include in master.")
	fname = get_filelist()
	
	return generic_reader(fname)


def head_lookup(donor_h, main_h):
	"""
	create lookup dictionary for inputted headers
	"""
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


def star_listing(donor_dat, mst_dat, mode):
	"""
	Create dict of star:new-line-index
	for all donor file stars in hst data
	"""
	mst_nam = [w[0] for w in mst_dat]
	if not mode:
		mst_id = mst_nam
	else:
		mst_id = [x[mode].strip() for x in mst_dat]
	donor_id = [y[0] for y in donor_dat]
		
	name_dict = {}
	for num, iden in enumerate(mst_id):
		if not iden:
			print("Skipping a case of missing identifier!")
			continue
		idlist = [i for i,xchk in enumerate(donor_id) if iden in xchk]
		if len(idlist) == 1:
			name_dict[mst_nam[num]] = idlist[0]
		elif len(idlist) == 0:
			pass
		else:
			print("Multiple matching entried found for {}".format(iden))
			for j,q in enumerate(idlist): print(j, donor_dat[q])
			indx = int(input("Give index of preferred match: "))
			name_dict[mst_nam[num]] == idlist[indx]
	
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


def get_filename():
	# Get savename from user
	# check only 1 extension given
	fnm = ""
	while not fnm:
		fnm = input("Give name for save file (no extension):\n") + '.csv'
	
	return fnm


def save_master_csvfile(headers, data_lists, mst_name):
	# write headers and data to master file
	with open(mst_name, 'w') as fout:
		fwrt = csv.writer(fout, delimiter = ',')
		fwrt.writerow(headers)
		fwrt.writerows(data_lists)
	print("Data saved to {}!".format(mst_name))


# MAIN  ################################################################

# get master file
master_heads, master_data =  master_reader()
# get donor file

# define new headers and new data
donor_heads, donor_data = donor_reader()

# obtain cross reference dictionary for headers and for stars
cross_ref = head_lookup(donor_heads, master_heads)
# need option to look up by coordinates #########################################
sortmode = ""
print("Donor file has star identifiers such as:")
eg = [donor_data[x][0] for x in [3,6,9]]
for l in eg: print(l)

while sortmode not in ("n", "c"):
	sortmode = input("Choose star sorting mode - names or coordinates (n/c): ").lower()
if sortmode == "n":
	sortmode = 0
elif sortmode == "c":
	sortmode = 4
star_ref = star_listing(donor_data, master_data, sortmode)

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

