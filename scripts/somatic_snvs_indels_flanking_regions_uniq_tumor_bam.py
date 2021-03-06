import sys
import os
from os import listdir
import subprocess
from subprocess import check_output
import re
import time
from difflib import SequenceMatcher
from Bio import motifs
from Bio.Seq import Seq
from pyfaidx import FastaVariant

# infile
infile = sys.argv[1]

# reference files
galgal5_fa = "/home/proj/MDW_genomics/steepale/galgal5/galgal5.fa"

# Add bam files to set
bams = set()
for bamfile in listdir("/home/proj/MDW_genomics/xu/final_bam"):
	if re.search("bam$", bamfile):
		bams.add("/home/proj/MDW_genomics/xu/final_bam/" + bamfile)

# outfiles
outfile = open(sys.argv[2], 'w')
delinquent_file = open("./data/delinquent_sequences_vars.txt" , 'w')

# Create a header for output file
outfile.write('#Explanation of headers' + '\n')	
outfile.write('#CHROM:'+' '+'Chromosome' + '\n')
outfile.write('#POS:'+' '+'Position(s)' + '\n')
outfile.write('#REF:'+' '+'Reference allele' + '\n')
outfile.write('#ALT:'+' '+'Alternative allele' + '\n')
outfile.write('#VARIANT_TYPE:'+' '+'Mutation type' + '\n')
outfile.write('#SAMPLE:'+' '+'Samples with mutation' + '\n')
outfile.write('#DOWNSTREAM_POS:'+' '+'Downstream region of 100 bp flanking region' + '\n')
outfile.write('#UPSTREAM_POS:'+' '+'Upstream region of 100bp flanking region' + '\n')
outfile.write('#IUPAC_CONSENSUS_SEQ_100BP_DOWNSTREAM:'+' '+'Downstream 100bp flanking sequence as a IUPAC flanking sequence' + '\n')
outfile.write('#SOMATIC_VARIANT:'+' '+'The sequence of the alternative allele but in a unique format' + '\n')
outfile.write('#IUPAC_CONSENSUS_SEQ_100BP_UPSTREAM:'+' '+'Upstream 100bp flanking sequence as a IUPAC flanking sequence' + '\n')
outfile.write('#SIMILARITY:'+' '+'Similarity of consensus sequences to reference sequence counterparts' + '\n')
outfile.write('#CHROM'+'\t'+'POS'+'\t'+'REF'+'\t'+'ALT'+'\t'+'VARIANT_TYPE'+'\t'+'SAMPLE'+'\t'+'DOWNSTREAM_POS'+'\t'+'UPSTREAM_POS'+'\t'+'IUPAC_CONSENSUS_SEQ_100BP_DOWNSTREAM'+'\t'+'SOMATIC_VARIANT'+'\t'+'IUPAC_CONSENSUS_SEQ_100BP_UPSTREAM'+'\t'+'SIMILARITY'+'\n')

# Function for sequence matching similarity
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Define sets
delinq_set = set()
var2sam2flank_set = set()

# iterate through infile and capture variables
for inline in open(infile):
	if inline[0] != '#':
		inline = inline.rstrip()
		incol = inline.split('\t')
		inchr = incol[0]
		inpos = incol[1]
		inref = incol[2]
		inalt = incol[3]
		invar = inchr +'\t'+ inpos +'\t'+ inref +'\t'+ inalt
		insample = incol[11]
		sam = insample.split(';')
		# write the int variant file in basic bed format for a single variant position from reference sequence
		if len(inref) == 1 and len(inalt) == 1:
			inmut = 'SNV'
			start_var = int(inpos) - 1
			end_var = int(inpos)
			som_var = inalt
		elif len(inref) > 1:
			inmut = 'DEL'
			start_var = int(inpos) - 1
			end_var = int(inpos) + len(inref) - 1
			som_var = inref[0] + '-'*(len(inref) - 1)
		elif len(inalt) > 1:
			inmut = 'INS'
			start_var = int(inpos) - 1
			end_var = int(inpos) + len(inalt) - 1
			som_var = inref[0] + '+'*(len(inalt) -1)
		outfile_bed = "./data/somatic_var_bed.bed"
		outfile_bed = open(outfile_bed, 'w')
		outfile_bed.write(inchr + '\t' + str(start_var) + '\t' + str(end_var) + '\n')
		outfile_bed.close()
		# Use samtools mpileup to query the galgal5 reference file
		bedtools_var_cmd = "bedtools getfasta -fi "+galgal5_fa+" -bed ./data/somatic_var_bed.bed"
		# Use subprocess.Popen to ellicit shell commands 
		bedtools_var_proc = subprocess.Popen([bedtools_var_cmd], stdout=subprocess.PIPE, shell=True)
		# Use communicate to capture the output in a 'bytes' object
		(var_out, var_err) = bedtools_var_proc.communicate()
		# Decode the 'bytes' object to a string
		bedtools_var_out = var_out.decode("utf-8").rstrip().split('\n')[1]
		ref_var_out = bedtools_var_out
		#print('Variant' +' \t' + invar + '\t' + inmut)
		#print('ref_var_out ' + ref_var_out)

		# write the int downstream file in basic bed format for 100 bp downstream of single var position from reference sequence
		# For each upstream and downstream sequence:
		for sample in sam:
			for flank in ['up', 'down']:
				if flank == 'up':
					start_flank_0 = int(inpos) + len(inref) - 1
					end_flank_0 = start_flank_0 + 100
					start_flank_1 = start_flank_0 + 1
					end_flank_1 = end_flank_0 + 1
				elif flank == 'down':
					start_flank_0 = start_var - 100
					end_flank_0 = start_var
					start_flank_1 = start_var - 100
					end_flank_1 = start_var
				# Create the bed file to query tumor bam
				outfile_flank = "./data/somatic_var_flank.bed"
				outfile_flank = open(outfile_flank, 'w')
				outfile_flank.write(inchr + '\t' + str(start_flank_0) + '\t' + str(end_flank_0) + '\n')
				outfile_flank.close()
				# Bedtools getfasta command
				bedtools_flank_cmd = "bedtools getfasta -fi "+galgal5_fa+" -bed ./data/somatic_var_flank.bed"
				# Use subprocess.Popen to ellicit shell commands 
				bedtools_flank_proc = subprocess.Popen([bedtools_flank_cmd], stdout=subprocess.PIPE, shell=True)
				# Use communicate to capture the output in a 'bytes' object
				(flank_out, flank_err) = bedtools_flank_proc.communicate()
				# Decode the 'bytes' object to a string
				ref_flank_out = flank_out.decode("utf-8").rstrip().split('\n')[1]
				# Iterate over bam files to collect downstream primer sequence for each sample
				for bamfile in bams:
					var2sam2flank = invar + sample + flank
					if re.search(sample, bamfile) and var2sam2flank not in var2sam2flank_set:
						# Add variants and associated tumor sample to set to avoid redundency
						var2sam2flank_set.add(var2sam2flank)
						# Create a samtools command to create a intermediate bam file of region of interest
						samtools_view_cmd = "samtools view -ub "+bamfile+" "+inchr+":"+str(start_flank_1)+"-"+str(end_flank_1)+" > ./data/int_flank.bam"
						os.system(samtools_view_cmd)
						samtools_index_cmd = "samtools index ./data/int_flank.bam"
						os.system(samtools_index_cmd)
						# Samtools and mpileup work together to call variants at region of interest
						samtools_mpileup_flank_cmd = "samtools mpileup -uf "+galgal5_fa+" ./data/int_flank.bam -d 5000 | bcftools call -c -Oz -o ./data/int_flank.vcf.gz"
						os.system(samtools_mpileup_flank_cmd)
						# Tabix index the vcf
						tabix_flank_cmd = "tabix -f -p vcf ./data/int_flank.vcf.gz"
						os.system(tabix_flank_cmd)
						# Filter low quality calls
						filter_cmd = "bcftools filter -O z -o ./data/int_flank_filter.vcf.gz -s LOWQUAL -i'%QUAL>10' ./data/int_flank.vcf.gz"
						os.system(filter_cmd)
						# Index again
						tabix_filter_cmd = "tabix -f -p vcf ./data/int_flank_filter.vcf.gz"
						os.system(tabix_filter_cmd)

						# Determine the consensus sequence of the region of interest using ref chr and vcf file
						with FastaVariant("/home/proj/MDW_genomics/steepale/galgal5/contig_fastas/"+inchr+".fa", './data/int_flank_filter.vcf.gz', het=True, hom=True) as consensus:
							for chromosome in consensus:
								if flank == 'down':
									site = int(end_flank_1)
								elif flank == 'up':
									site = int(end_flank_1 - 1)
								bam_flank_100 = chromosome[site-100:site]
								final_flank_out = bam_flank_100.seq
								# Check for the accuracy of each sample's 100bp sequence with that of the reference sequence
								similarity = similar(ref_flank_out, final_flank_out)
							if similarity < 1  and flank == 'down' and invar not in delinq_set:
								delinq_set.add(invar)
								delinquent_file.write('\n' + invar + '\n')
								delinquent_file.write('Downstream Reference Sequence:' + '\n' + ref_flank_out + '\n')
								delinquent_file.write(bamfile + ' SIMILARITY: ' + str(similarity) + '\n' + final_flank_out + '\n')
							elif similarity < 1 and flank == 'down' and invar in delinq_set:
								delinquent_file.write(bamfile + ' SIMILARITY: ' + str(similarity) + '\n' + final_flank_out + '\n')
							if similarity < 1  and flank == 'up' and invar not in delinq_set:
								delinq_set.add(invar)
								delinquent_file.write('\n' + invar + '\n')
								delinquent_file.write('Upstream Reference Sequence:' + '\n' + ref_flank_out + '\n')
								delinquent_file.write(bamfile + ' SIMILARITY: ' + str(similarity) + '\n' + final_flank_out + '\n')
							elif similarity < 1 and flank == 'up' and invar in delinq_set:
								delinquent_file.write(bamfile + ' SIMILARITY: ' + str(similarity) + '\n' + final_flank_out + '\n')
							# create a IUPAC consensus sequence
							consensus_flank = final_flank_out
							if flank == 'up':
								consensus_upstream = str(consensus_flank)
								similarity_up = similar(ref_flank_out, consensus_upstream)
								upstream_pos = inchr+':'+str(start_flank_1)+'-'+str(end_flank_1 - 1)
							elif flank == 'down':
								consensus_downstream = str(consensus_flank)
								similarity_down = similar(ref_flank_out, consensus_downstream)
								downstream_pos = inchr+':'+str(start_flank_1 + 1)+'-'+str(end_flank_1)

			outfile.write(inchr+'\t'+inpos+'\t'+inref+'\t'+inalt+'\t'+inmut+'\t'+sample+'\t'+downstream_pos+'\t'+upstream_pos+'\t'+consensus_downstream+'\t'+som_var+'\t'+consensus_upstream+'\t'+str(similarity_down)+';'+str(similarity_up)+'\n')

outfile.close()
