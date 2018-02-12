#!/usr/bin/env python

"""usage:
        gc_correct.py [options] counts.txt

    where the options are:
        -h,--help : print usage and quit
        -d,--debug: print debug information
        -v,--version: print version and exit
        -o,--output: write the corrected counts to this file [stdout]

   where the arguments are:
        counts.txt : a tab delimited file with chromosome, start, stop, GC, counts
                   for bins that have the same size
"""

from sys import argv, stderr, exit
from getopt import getopt, GetoptError
from time import time
import numpy as np
import pandas as pd
from statsmodels.robust.scale import mad
import os.path, logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(message)s"
)
logging.disable(logging.DEBUG)

def correct_counts(counts_file_name):
    """Calculate corrected reads depth values over bins

    Args:
        counts_file_name (str): name of tab delimited file with chromosome, start, stop, GC, counts
                   for bins that have the same size

    Returns:
        data (pandas.DataFrame): data frame with data from input file and corrected counts values in column 'updated'

    """
    if not os.path.isfile(counts_file_name):
        raise IOError("File %s does not exists" % counts_file_name)

    data = pd.read_table(counts_file_name,
                         names=['chrom', 'start', 'stop', 'gc', 'counts'],
                         dtype={'chrom': np.str,
                                'start': np.int32,
                                'stop': np.int32,
                                'gc': np.int32,
                                'counts': np.int32})

    logging.debug("Input file %s loaded" % counts_file_name)

    if data.empty:
        logging.debug("Input file is empty!")
        return data

    bin_length = data.apply(lambda row: row['stop'] - row['start'], axis=1)
    if len(bin_length.unique()) != 1:
        logging.debug("Warning: Bins of different sizes!")

    median_all = np.median(data['counts'])
    mad_all = mad(data['counts'])

    median_gc_bins = {}  # gc count in bin: median over all bins with the same gc count
    for gc in data.gc.unique():
        median_gc_bins[gc] = float(np.median(data.loc[data['gc'] == gc]['counts']))

    logging.debug("Median of counts over all bins: %s" % median_all)
    logging.debug("MAD of counts over all bins: %s" % mad_all)
    logging.debug("Calculating corrected reads depth values over bins")

    data['updated'] = data.apply(
        lambda row: row['counts'] * median_all / median_gc_bins[row['gc']] if median_gc_bins[row['gc']] != 0 else 1.0,
        axis=1)

    return data


def main():
    start = time()
    version = "0.0.2"
    print_version = False
    out_file = None

    try:
        opts, args = getopt(argv[1:], "hdvo:b:", ["help", "debug", "version", "output="])
    except GetoptError, err:
        print >> stderr, str(err)
        print >> stderr, __doc__
        exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            print >> stderr, __doc__
            exit()
        elif o in ("-d", "--debug"):
            logging.disable(logging.NOTSET)
            logging.debug("Debug mode activated")
        elif o in ("-v", "--version"):
            print_version = True
        elif o in ("-o", "--output"):
            out_file = a

    if print_version:
        print >> stderr, "Program: GC Correct"
        print >> stderr, "Version: %s" % version
        print >> stderr, "Contact: ..."
        exit(0)

    if len(args) != 1:
        print >> stderr, __doc__
        exit(2)

    corrected = correct_counts(args[0])

    if out_file:
        logging.debug("Saving results to %s" % out_file)
        corrected.to_csv(out_file, header=None, index=None, sep='\t')
    else:
        print corrected

    logging.debug("Elapsed time: %s [s]" % str(time() - start))


if __name__ == "__main__":
    main()
