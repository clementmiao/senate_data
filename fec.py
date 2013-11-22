
## Clement Miao

import string
from pylab import *
import matplotlib
import numpy
import pylab



# defined constants for candidate field numbers
CAND_NAME = 0
CAND_PCC = 1
CAND_PARTY = 2
CAND_HOME_STATE = 3
CAND_ZIPCODE = 4
CAND_CONTRIBUTIONS = 5

rep = 0
def parse_candidate_line(line):
  line = line.strip().split("|")
  name = line[CAND_NAME]
  pcc = line[CAND_PCC]
  party = line[CAND_PARTY].upper()
  home_state = line[CAND_HOME_STATE]
  zipcode = line[CAND_ZIPCODE]
  return (name, pcc, party, home_state, zipcode, [])

def read_candidate_data(fn):
  ''' 
  Read in the candidate data.

  returns: dictionary that maps candidate PCC to list with candidate
  information.
  '''
  name_to_pcc = {}
  pcc_to_cand_info = {}
  no_pccs = 0
  for line in open(fn).readlines():
    cand = parse_candidate_line(line)
    name = cand[CAND_NAME]
    pcc = cand[CAND_PCC]
    if pcc == "":
      print "Dropping candidate with empty PCC:", name,":"
      no_pccs = no_pccs + 1
    elif pcc not in pcc_to_cand_info:
      pcc_to_cand_info[pcc] = cand

    if name in name_to_pcc:
      name_to_pcc[name].append(pcc)
    else:
      name_to_pcc[name] = [pcc]

  print "Dropped: ", no_pccs, " candidates without a PCC"
  return (name_to_pcc, pcc_to_cand_info)




# defined constants for contribution field numbers

CONTR_COMMITTEE_ID = 0      # matches PCC in candidate records
CONTR_AMOUNT = 1
CONTR_STATE = 2
CONTR_ZIPCODE = 3

def convert_int(s):
  '''
  Try to convert a string to an integer.
  
  Input: a string

  Output: an integer or a string

  Examples:
    convert_int("27") returns 27
    convert_int("cs121") returns "cs121"
  '''
  try:
    return int(s)
  except:
    return 0


def add_contributions_data(pcc_to_cand_info, fn):
  '''
  Read in the contribution data

  Adds contribution data to exisiting candidates.  Add all data
  for unknown candidates to a candidate named "UNKNOWN".
  '''
  cnt = 0
  for line in open(fn).readlines():
    cont = line.strip().split("|")
    cont[CONTR_AMOUNT] = convert_int(cont[CONTR_AMOUNT])
    pcc = cont[CONTR_COMMITTEE_ID]
    if pcc == "":
      print "Dropping contribution with empty pcc"
      cnt = cnt + 1
    elif pcc in pcc_to_cand_info:
      pcc_to_cand_info[pcc][CAND_CONTRIBUTIONS].append(cont)
    else:
      print "Dropping contribution to:" + str(pcc) +":"
      cnt = cnt + 1
  print "Dropped: ", str(cnt), " contributions"



def read_data(cand_filename, cont_filename):
  (name_to_pcc, pcc_to_cand_info) = read_candidate_data(cand_filename)
  add_contributions_data(pcc_to_cand_info, cont_filename)
  return pcc_to_cand_info


def mk_zip_code_map():
  '''
  Parse zip code data

  Returns: map from zipcode to (latitude, longitude)
  '''
  rv = {}
  for z in open("zipcodes/zipcode.csv").readlines()[1:]:
    z = z.strip(string.whitespace)
    if z == "":
      continue
    zip = z.strip().split(",")
    zipcode = zip[0][1:-1]
    lat = pylab.double(zip[3][1:-1])
    lon = pylab.double(zip[4][1:-1])
    rv[zipcode] = (lat,lon)
  return rv


LOWER48_EASTMOST_LONGITUDE = -66.57
LOWER48_WESTMOST_LONGITUDE = -124.46
LOWER48_NORTHMOST_LATITUDE = 49.2341
LOWER48_SOUTHMOST_LATITUDE = 24.3115


### END OUR CODE


# Task 1 
def total_contributions_to_candidate(candidate_info):
  '''
  Returns the total amount of contributions the candidate received
  from in-state and out-of-state contributors
  '''
  contributions_list = candidate_info[CAND_CONTRIBUTIONS]
  h_state = candidate_info[CAND_HOME_STATE]
  in_state = 0
  out_state = 0
  for x in contributions_list:
    s = x[CONTR_STATE]
    a = x[CONTR_AMOUNT]
    if s == h_state:
      in_state += a 
    else:
      out_state += a
  return (in_state, out_state)



# Task 2
def scatter_plot_by_contributor(candidate_info, filename):
  '''
  Draws a scatter plot of a the contributions a candidate received from
  contributors in the lower 48 states.  Saves the result in the specified
  file.
  '''
  dictionary = mk_zip_code_map()
  contributions_list = candidate_info[CAND_CONTRIBUTIONS]
  x_val = []
  y_val = []
  for x in contributions_list:
    if x[CONTR_ZIPCODE] in dictionary:
      if dictionary[x[CONTR_ZIPCODE]][1] < LOWER48_EASTMOST_LONGITUDE and dictionary[x[CONTR_ZIPCODE]][1] > LOWER48_WESTMOST_LONGITUDE and dictionary[x[CONTR_ZIPCODE]][0] < LOWER48_NORTHMOST_LATITUDE and dictionary[x[CONTR_ZIPCODE]][0] > LOWER48_SOUTHMOST_LATITUDE:
        x_val.append(dictionary[x[CONTR_ZIPCODE]][1])
        y_val.append(dictionary[x[CONTR_ZIPCODE]][0])  
  figure(1)
  plot(x_val, y_val, 'bx')
  if candidate_info[CAND_ZIPCODE] in dictionary:
    plot( dictionary[candidate_info[CAND_ZIPCODE]][1] , dictionary[candidate_info[CAND_ZIPCODE]][0], 'ro')
  xlabel('Longitude') 
  ylabel('Latitude')
  title('Contributions to ' + candidate_info[CAND_NAME])
  savefig(filename)
  close('all')



# TASK 3
def num_candidates_in_party(pcc_to_cand_info, party):
  ''' 
  Given the candidate data structure, returns the number of candidates that
  belong to the specified party.
  '''
  party = party.upper()
  count = 0
  for key in pcc_to_cand_info.keys():
    cand = pcc_to_cand_info[key]
    if cand[CAND_PARTY] == party:
      count += 1
  return count

## Task 4:
def create_pie_chart_of_party_fractions(pcc_to_cand_info, threshold, filename):
  '''
  Given the candidate data, creates a pie chart of the fraction of
  candidates from each party that has at least threshold candidates.
  Lumps all parties that have fewer than threshold candidates into a
  single "below_threshold" category.  Saves the result in the
  specified file.
  '''
  dictionary = {}
  for value in pcc_to_cand_info.values():
    party = value[CAND_PARTY]
    if party in dictionary:
      dictionary[party] += 1
    else:
      dictionary[party] = 1
  total = sum(dictionary.values())
  test = 0
  final_dictionary = {}
  for key, value in dictionary.items():
    v = (value / float(total)) * 100
    if value < threshold:
      if 'below threshold' not in final_dictionary:
        final_dictionary['below_threshold'] = v
      else:
        final_dictionary['below_threshold'] += v
    else:
      final_dictionary[key] = v
  fracs = []
  labels = []
  for key, value in final_dictionary.items():
    fracs.append(value)
    labels.append(key)
  figure(2, figsize=(6,6))
  ax = axes([0.1, 0.1, 0.8, 0.8])
  pie(fracs, labels = labels)
  title('Fraction of candidates in each party (threshold:' + str(threshold) + ')')
  savefig(filename)
  close('all')


# Task 5
def identify_cands_with_higher_out_vs_in_contributions(pcc_to_cand_info):
  '''
  Given the candidates data structure, returns a list of the names of
  candidates who received more money from out-of-state than from
  in-state contributors.
  '''
  candidates_list = []
  for x in pcc_to_cand_info.values():
    home = x[CAND_HOME_STATE]
    in_count = 0
    out_count = 0
    contributions = x[CAND_CONTRIBUTIONS]
    for y in contributions:
      s = y[CONTR_STATE]
      a = y[CONTR_AMOUNT]
      if s == home:
        in_count += a 
      else:
        out_count += a
    if out_count > in_count:
      candidates_list.append(x[CAND_NAME])

  return candidates_list


## Task 6
def create_bar_chart_contributions_by_state(pcc_to_cand_info, filename):
  '''
  Given the candidate data, generates a barchart by total contributions
  by state and save the result in the specified file.
  '''
  dictionary = {}
  for x in pcc_to_cand_info.values():
    contributions_list = x[CAND_CONTRIBUTIONS]
    for i in contributions_list:
      s = i[CONTR_STATE]
      a = i[CONTR_AMOUNT]
      if s not in dictionary:
        dictionary[s] = a
      else:
        dictionary[s] += a
  y_values = []
  x_values = []
  for key in sorted(dictionary):
    x_values.append(key)
    y_values.append(dictionary[key])
  figure(3)
  ax = subplot(111)
  ax.bar(arange(len(x_values)), y_values, width = 0.9)
  ax.set_xticks(arange(len(x_values)) + 0.9)
  ax.set_xticklabels(x_values, rotation = 90)
  ax.ticklabel_format(axis = 'y', style = 'sci', scilimits = ( 0,0 ))
  xlabel('State')
  ylabel('Contributions in millions')
  title('Total contributions by contributor\'s home state')
  savefig(filename)
  close('all')

  





