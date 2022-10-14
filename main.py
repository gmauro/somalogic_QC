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
            extid_counts = Counter(adat.index.get_level_values('SsfExtId'))
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
            somaid_entries_duplicated = [(k, v) for k, v in somaid_entries_counts.items() if v > 1]
            logger.info('Found {} SomaId entries duplicated'.format(len(somaid_entries_duplicated)))
            # logger.info('They are: {}'.format(somaid_entries_duplicated))

            buffer_adat = adat.pick_on_meta(axis=0, name='SampleType', values=['Buffer'])
            # print(buffer_adat.pick_on_meta(axis=1, name='SeqId', values=['2780-35']).reset_index(drop=True).max())
            target_2780_35 = buffer_adat.pick_on_meta(axis=1, name='SeqId', values=['2780-35']).reset_index(drop=True)
            min = target_2780_35.min()
            max = target_2780_35.max()
            std = target_2780_35.std()
            mean = target_2780_35.mean()
            median = target_2780_35.median()
            q1 = target_2780_35.quantile(q=0.25)
            q3 = target_2780_35.quantile(q=0.75)
            cov = std/mean.abs()
            print(min.values, q1.values, mean.values, median.values, q3.values, max.values)

            targets = buffer_adat.exclude_on_meta(axis=0, name='RowCheck', values=['FLAG']).pick_meta(axis=1, names=['SeqId']).reset_index(drop=True)
            min = targets.min()
            max = targets.max()
            std = targets.std()
            mean = targets.mean()
            median = targets.median()
            q1 = targets.quantile(q=0.25)
            q3 = targets.quantile(q=0.75)
            cov = std / mean.abs()
            cv_02 = 0
            cv_1 = 0
            for c in cov.values:
                if c >= 0.2:
                    cv_02 += 1
                if c >= 1:
                    cv_1 += 1
            print(cv_02, cv_1)
            print(cov.values)
            # print(target_2780_35.mean(), target_2780_35.var())
            # print([v for v in target_2780_35.columns.get_level_values('SeqId')])

            # Extract columns containing features that start with 'MMP'
            # target_names = adat.columns.get_level_values('Target')
            # mmp_names = [target for target in target_names if target.startswith('MMP')]
            # mmp_adat = adat.pick_on_meta(axis=1, name='Type', values=mmp_names)
    else:
        logger.error('{} path not found'.format(args.data_path))
        exit()


if __name__ == '__main__':
    main()
