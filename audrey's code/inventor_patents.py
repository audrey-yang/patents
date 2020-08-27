#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inventor + Year to Patents

This script links inventors to their patents and those patents' citations.

The files produced are outputs/inventor_year_patents_bk.csv and 
outputs/inventor_year_patents_fw.csv, with header:
    inventor_id, year, patent_id, citation_id, subsection_id

@author: Audrey Yang (auyang@seas.upenn.edu)
"""

import time
import csv

print('***\nBEGIN PROCESS')
start_time = time.ctime()

# Load cpc_current
cpc_current_file = open('../patent_data/cpc_current.tsv', 
                            encoding='utf-8-sig')
cpc_current = csv.DictReader(cpc_current_file, delimiter='\t')

# Create patent to subsection_id and sequence dictionary
print('Creating subsection dict\n...') 
patent_to_subsection = {}
for row in cpc_current:
    if row['sequence'] == '0':
        patent_to_subsection[row['patent_id']] = row['subsection_id']
    
# Load patent
patent_file = open('../patent_data/patent.tsv', 
                        encoding='utf-8-sig')
patent = csv.DictReader(patent_file, delimiter='\t') 
    
# Create patent to year dictionary
print('Creating year dict\n...')
patent_to_year = {}
for row in patent:
    patent_to_year[row['number']] = int(row['date'][:4])
 
# Load uspatentcitation
uspatentcitation_file = open('../patent_data/uspatentcitation.tsv', 
                            encoding='utf-8-sig')
uspatentcitation = csv.DictReader(uspatentcitation_file, delimiter='\t')

# Year range (for forward citations)
year_range = 7

# Create patent to citation dictionary, fw and bk
print('Creating citations dict\n...')
patent_to_citationbk = {}
patent_to_citationfw = {}
for row in uspatentcitation:
    # Adding to backward citations
    lstbk = patent_to_citationbk.get(row['patent_id'], [])
    lstbk.append(row['citation_id'])
    patent_to_citationbk[row['patent_id']] = lstbk
    
    # Adding to forward citations
    if row['date']:
        if patent_to_year.get(row['patent_id'],  
                              20000) - int(row['date'][:4]) <= year_range:
            lstfw = patent_to_citationfw.get(row['citation_id'], [])
            lstfw.append(row['patent_id'])
            patent_to_citationfw[row['citation_id']] = lstfw

# Load inventor_patent
inventor_to_patent_file = open('../outputs/inventor_patent.csv', 
                               encoding='utf-8-sig')
inventor_to_patent = csv.DictReader(inventor_to_patent_file)

# Write to output file
print('Creating output files\n...')
with open(
        '../outputs/inventor_year_patents_bk.csv', 'w', newline="\n", encoding='utf-8-sig'
        ) as output_bk_file, open(
        '../outputs/inventor_year_patents_fw.csv', 'w', newline="\n", encoding='utf-8-sig'
        ) as output_fw_file:
    output_bk = csv.writer(output_bk_file, delimiter=',')
    output_fw = csv.writer(output_fw_file, delimiter=',')
    header = ['inventor_id', 'year', 'patent_id', 'citation_id', 'subsection_id']
    output_bk.writerow(header)   
    output_fw.writerow(header)   

    for row in inventor_to_patent:
        # Writing backward citations
        patent = row['patent_id']
        for cit in patent_to_citationbk.get(patent, []):
            output_bk.writerow([
                row['inventor_id'], 
                patent_to_year.get(patent, 'N/A'),
                patent,
                cit,
                'Design' if cit[0] == 'D' else (
                        patent_to_subsection.get(cit, 'N/A')),
            ]) 
        
        # Writing forward citations
        for cit in patent_to_citationfw.get(patent, []):
            output_fw.writerow([
                row['inventor_id'], 
                patent_to_year.get(patent, 'N/A'),
                patent,
                cit,
                'Design' if cit[0] == 'D' else (
                        patent_to_subsection.get(cit, 'N/A')),
            ]) 
    
print('***\nEND OF PROCESS')
end_time = time.ctime()

print('Start Time: ' + start_time)
print('End Time: ' + end_time)