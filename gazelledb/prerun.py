'''
Tool to compute nodes beforehand to avoid long delays when accessed through
web.
'''
from pymongo import MongoClient
mongo = MongoClient()
db = mongo.gazelle

import logging
logger = logging.getLogger('prerun')
import coloredlogs
coloredlogs.install(level=logging.DEBUG, show_timestamps=False, show_hostname=False)

from lib import get_node

def main():
    logger.info('Starting...')

    # By computing the nodes, the results are cached.
    policy = 'ensure'
    root_nodes = [
        'icl/cg/nonconvergent/',
    ]
    for rn in root_nodes:
        logger.info('Running ' + rn)
        computed_node = get_node.by_name_computed(db, rn, policy)
        if computed_node is None:
            logger.error('Does not exist: ' + rn)

    logger.info('Done.')

if __name__ == '__main__':
    main()
