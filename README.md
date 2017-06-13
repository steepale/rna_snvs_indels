We have received variant SNV and INDEL calls from our RNASeq data from a collaboration with the Grigoriev Lab at Rutgers. This project aims to compare those calls from their software, GROM, with our calls from multiple SNV and INDEL callers, both somatic and germline.

For step-by-step documentation see rna_snv_indels_main_documentation.txt

The Grigoriev Lab contacted us in May, 2017 with somatic non-synoymous snvs and indel calls from GROM. What is especially unique about these calls is that they represent both mutated dna and rna. We provided them with a list of all of our possible candidates, about 650 variants, with the assumption that false positives were in these variants. To our surprise, the results from GROM yielded only 18 variants. Even considering that many genomic mutations may not be expressed through rna in the CD4+ cell environment, this number seemed low. We aimed to replicate this analysis through different means.

In this analysis we used samtools to queury transcriptome aligned bam files (Galgal5 reference genome) for the presence of our 650 genomic variants. Our results, which yeilded 9 variants, agreed with those of GROM. Our flagship driver gene was expressed in both results, leading us to have a higher degree of confidence in GROM results. We will aim to validate DNA variants and possibly select RNA variants.
 


