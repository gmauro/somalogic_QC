# Count the number of columns
# awk -F'\t' '{print NF}' example_data.adat| sort -nu | tail -n 1

import argparse
import canopy
import pathlib

from collections import Counter
from comoda import a_logger, LOG_LEVELS


class App:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog='somalogic_QC',
                                              description='Check routines for Somalogic adat files')
        self.parser.add_argument('--data_path', type=str, required=True, metavar='PATH',
                                 help='Path where adat files are')
        self.parser.add_argument('--ext', type=str, help='file extension', default=".adat")
        self.parser.add_argument('--logfile', type=str, metavar='PATH', help='log file')
        self.parser.add_argument('--loglevel', type=str, help='logger level.', choices=LOG_LEVELS, default='INFO')


def main():
    app = App()
    parser = app.parser
    args = parser.parse_args()
    logger = a_logger('Main', level=args.loglevel, filename=args.logfile)
    logger.info('{} started'.format('Somalogic datasets check'))

    if pathlib.Path(args.data_path).exists():
        adat_file_paths = list(pathlib.Path(args.data_path).rglob(''.join(['*', args.ext])))
        logger.info('{} {} files found in {}'.format(len(adat_file_paths), args.ext, args.data_path))

        for fp in adat_file_paths:
            logger.info('***')
            logger.info('Checking {}'.format(fp))
            adat = canopy.read_adat(str(fp))
            shape = adat.shape[1]
            counters = adat.index.get_level_values('SampleType')
            logger.info('{} targets found.'.format(shape))
            logger.info('Counts of sample types: {}'.format(Counter(counters)))
    else:
        logger.error('{} path not found'.format(args.data_path))
        exit()


if __name__ == '__main__':
    main()
