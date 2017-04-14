import sys
import os

# Input files
dna_file = open("./data/somatic_snvs_and_indels_final.txt") 
rna_file = open("./data/wgs_rnaseq_overlap_r4indel_filter6_header.txt")

for dna_line in dna_file:
	dna_line = dna_line.rstrip()
	if dna_line[0] != '#':
		dna_col = dna_line.split('\t')
		dna_chr = dna_col[0]
		dna_pos = dna_col[1]
		dna_tsn = dna_col[8]
		dna_samples = dna_col[9]
		if dna_tsn == '1':
			dna_sample = dna_col[9]
			#print(dna_chr + '\t' + dna_pos + '\t' + dna_tsn + '\t' + dna_sample + '\n')
			for rna_line in rna_file:
				rna_line = rna_line.rstrip()
				if rna_line != '#':
					rna_col = rna_line.split('\t')
					rna_chr = rna_col[4]
					rna_pos = rna_col[5]
					print('rna_chr ' + rna_chr)
					print('rna_pos ' + rna_pos)
					print('dna_chr ' + dna_chr)
					print('dna_pos ' + dna_pos)
					if rna_chr == dna_chr and rna_pos == dna_pos:
						print(dna_line)
						print(rna_line + '\n')
