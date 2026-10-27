# Preelimiary Remark
This README explains how we compute (quasi-)normal NTFS timestamp structures under the restriction that the RE operation (modeling NTFS operations such as `Rename`) occurs at most once in any composition of NTFS operations, and how we investigate their prevalence in disk images. The computed structures may not exhaust all structures satisfying the formal definitions. For a full discussion, see our paper:

Lorenz Hornung, Jesse Heyninck, and Harm van Beek, Stepping up NTFS Forensics: Computing Normal NTFS Timestamp Structures.

Please cite the paper when using this work. This implementation is released under the CC BY-NC 4.0 license.


# Normal and Quasi-Normal NTFS Timestamp Structures
In this part, we explain how we compute normal and quasi-normal NTFS timestamp structures under the restriction described below. Consequently, the computation may not identify all structures satisfying the formal definitions. Under this restriction, our implementation identifies 4,128 normal and 704 quasi-normal NTFS timestamp structures using Answer Set Programming (ASP).  

## NTFS Timestamp Structures
The New Technology File System (NTFS) is Windows' file system. For each file, NTFS provides eight timestamps represented as numerical values. If these values for the timestamps are compared, one obtains, what we call, a timestamp structure.

## Identifying Normal NTFS Timestamps Structures
Normal timestamp structures are those that can be obtained by regular NTFS behavior. To computationally determine whether a timestamp structure of a file is normal, we need to establish whether it can be obtained by applying a sequence of operations to an initial timestamp structure. Initial timestamp structures characterize the structures a file can have after being introduced into NTFS. 

### Modelling of NTFS File Operations
NTFS file operations alter these timestamp structures. We model these operations by characterizing their effect on timestamp structures. These characterization can be found in `search_normal_NTFS_TS.lp`. 

If a NTFS file operation generates a completely new timestamp structure, we model it as an initial timestamp structure. These initial timestamp structures are characterized in the file `initial_NTFS_TS.py`. This file can be found in folder `initial_NTFS_TS`.  The list of timestamp structures `ntfs_initial_TS` characterize the initial timestamp structures (without file tunneling), while `ntfs_initial_TS_FT` contains the initial timestamp structures due to file tunneling and `ntfs_initial_TS_CR` contains only the initial timestamp structure due to file creation. 


### Reduce Search Space due to Compositions of NTFS Operations
We restrict the compositions considered to those in which the operation `RE` (modeling NTFS operations such as `Rename`) occurs at most once. As shown in our paper, the effects of all such compositions can be represented by a defined set of 80 compositions: for any composition satisfying this restriction, one of these 80 compositions produces the same output set of timestamp structures for every input structure.

The file `generate_NTFS_compositions.py` generates these 80 compositions in a suitable manner for ASP. In `NTFS_compositions.py`, you can find the list of the generated compositions. Both files can be found in folder `NTFS_compositions`. 

### Search in ASP Implementation
For any pair of initial NTFS timestamp structure and one of the 80 compositions to be considered from `NTFS_compositions.py` (folder: `NTFS_compositions`), we search for the timestamp structures that can be obtained. The resulting structures are the normal NTFS timestamp structures identified under the current restriction.

This search is characterized in `search_normal_NTFS_TS.lp`. To automatically search for any of these pairs, we use the Python clingo API. Thereby, we search for each set of initial timestamp structures (`ntfs_initial_TS`, `ntfs_initial_TS_FT`, and `ntfs_initial_TS_CR`) independently. Running `compute_normal_NTFS_TS.py` performs the search for three sets of initial timestamp structure independently. Note that running `compute_normal_NTFS_TS.py` may take a few hours.

The identified normal NTFS timestamp structures are stored in `normal_NTFS_TS.py` (due to initial timestamp structures `ntfs_initial_TS`), `normal_NTFS_TS_FT.py` (due to initial timestamp structures `ntfs_initial_FT`), and `normal_NTFS_TS_CR.py` (due to initial timestamp structures `ntfs_initial_CR`). These files can be found in folder `normal_NTFS_TS`.

To compare the normal timestamp structures identified under the current restriction for the different sets of initial timestamp structures, run `compare_normal_NTFS_TS.py`. This file can be found in folder `normal_NTFS_TS`. 

## Identifying Quasi-Normal NTFS Timestamps Structures
Quasi-normal (T \ {'si_4', 'fn_4'}-normal) timestamp structures are those expected under certain restrictions. That is, timestamps structures expected from regular user behavior, but not considering any last-access timestamps. This allows us to model expected timestamps structures, if last access updating is turned on. For computing normal timestamp structures we expected that this to not be the case, as last access updating is turned off by default.

We compute quasi-normal NTFS timestamps structures under our restriction by restricting normal NTFS timestamp structures to T \ {'si_4', 'fn_4'}. This restriction is defined in `compute_restricted_normal_NTFS_TS.py` and quasi-normal (T \ {'si_4', 'fn_4'}-normal) are stored in `normal_NTFS_TS_restricted.py` found in the folder `normal_NTFS_TS`.


## Requirements 
To run the documents, clingo, an Answer Set Programming solver, is needed. 
Clingo can be obtained here: https://potassco.org/doc/start/


# Timestamp Structures Analysis

In this part, we elaborate on the empirical evaluation of NTFS disk images. For this, we explain on the workflow of processing NTFS Master File Table (MFT) files to analyze and extract timestamp structure information. The analysis compares timestamp structures found in disk images with the structures identified under the restriction described above; a structure not found in the computed set is not necessarily abnormal.

## Workflow Overview

Follow these steps to process an MFT file and extract timestamp structure statistics:

### Step 1: Extract the $MFT File

Extract the $MFT (Master File Table) from a forensic image and save it as a local file. The exact method depends on your forensic imaging tool, but the result should be a raw MFT file.

### Step 2: Convert MFT to JSON

Use [MFTECmd.exe](https://github.com/EricZimmerman/MFTECmd) to convert the extracted MFT file to JSON format:

```bash
MFTECmd.exe -f <the extracted mft file> --at true --json
```

**About MFTECmd.exe**: MFTECmd is a command-line tool by Eric Zimmerman that parses NTFS Master File Table (MFT) files from forensic images. It extracts and analyzes file metadata, including timestamps, file names, and other attributes, and outputs the results in various formats including JSON for further analysis.

This generates a JSON file containing the parsed MFT data. Flag at (true) forces MFTECmd to include all timestamps.

### Step 3: Label Timestamp Structures

Run `statistics_labeller_NTFS_TS.py` to process the JSON file and extend it with timestamp structure information:

```bash
python statistics_labeller_NTFS_TS.py <mft json input file> <csv output file>
```

This script analyzes the MFT JSON and creates a CSV file that includes detailed timestamp structure labels and classifications.

### Step 4: Collect Statistics

Use `statistics_compute_NTFS_TS.py` to analyze timestamp structures from one or multiple JSON files and generate a statistical overview:

```bash
python statistics_compute_NTFS_TS.py <csv file(s)>
```

This script processes the labeled timestamp structure data and produces a comprehensive statistical report covering the distribution and characteristics of timestamp structures found in the MFT data.

## Tips and Tricks

If you store the MFTs as '.mft' file in a folder named MFTs, you can create all JSONs at once:

```bash
find MFTs -name "*.mft" -exec \
  sh -c 'MFTECmd.exe -f $1  --at true --json . --jsonf ${1%.*}.json' sh {} \; 
  | tee MFTECmd-run.log
```

Next, you can do all the labelling at once too:

```bash
find MFTs -name "*.json" -exec \
  sh -c 'python3.exe statistics_labeller_NTFS_TS.py  $1 ${1%.*}-structured.json' sh {} \; 
  | tee timestamp_structure_labeller.log
```

To generate an aggregated statistical overview for all the MFTs:

```bash
python3.exe statistics_compute_NTFS_TS.py $(ls -1 MFTs/*-structured.json) | tee structure_statistics.log
```

## Results 

The disk images analyzed in this study are subject to third-party rights, which preclude us from distributing the corresponding MFT files or labeled JSON outputs. The aggregate statistics and identified timestamp structures are nevertheless provided in `COMBINED_statistics.log` found in folder `logs`. 


