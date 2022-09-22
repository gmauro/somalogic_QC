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
            sample_types = adat.index.get_level_values('SampleType')
            logger.info('{} targets found.'.format(shape))
            logger.info('Counts of sample types: {}'.format(Counter(sample_types)))

            # Extract flagged samples
            flagged_samples = adat.pick_on_meta(axis=0, name='RowCheck', values=['FLAG'])
            logger.info('{} samples are flagged (RowCheck=FLAG)'.format(len(flagged_samples)))
            logger.info('These are the IDs:\n{}'.format(flagged_samples.index.get_level_values('SampleId')))

            # Verify that external IDs are unique
            extid_counts = Counter(adat.index.get_level_values('ExtIdentifier'))
            extid_duplicated = [k for k, v in extid_counts.items() if v > 1]
            logger.info('Found {} ExtIdentifier items duplicated'.format(len(extid_duplicated)))
            logger.info('They are: {}'. format(extid_duplicated))

            # Verify that sample IDs are unique
            sample_id_counts = Counter(adat.index.get_level_values('SampleId'))
            sample_id_duplicated = [(k, v) for k, v in sample_id_counts.items() if v > 1]
            logger.info('Found {} SampleId items duplicated'.format(len(sample_id_duplicated)))
            logger.info('They are: {}'.format([k for k in sample_id_duplicated]))

            # Verify UniProt entries are unique
            uniprot_entries_counts = Counter(adat.columns.get_level_values('UniProt'))
            uniprot_entries_duplicated = [k for k, v in uniprot_entries_counts.items() if v > 1]
            logger.info('Found {} UniProt entries duplicated'.format(len(uniprot_entries_duplicated)))
            #logger.info('They are: {}'.format(uniprot_entries_duplicated))

            # Verify Target entries are unique
            target_entries_counts = Counter(adat.columns.get_level_values('Target'))
            target_entries_duplicated = [k for k, v in target_entries_counts.items() if v > 1]
            logger.info('Found {} Target entries duplicated'.format(len(target_entries_duplicated)))

            # Verify SomaId entries are unique
            somaid_entries_counts = Counter(adat.columns.get_level_values('SomaId'))
            somaid_entries_duplicated = [k for k, v in somaid_entries_counts.items() if v > 1]
            logger.info('Found {} SomaId entries duplicated'.format(len(somaid_entries_duplicated)))

    else:
        logger.error('{} path not found'.format(args.data_path))
        exit()


if __name__ == '__main__':
    main()
