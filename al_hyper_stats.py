import argparse
import contextlib
import datetime
import io
import logging
import multiprocessing
import os
import random
import sys
from itertools import chain, combinations
from timeit import default_timer as timer

import numpy as np
import pandas as pd
import peewee
from evolutionary_search import EvolutionaryAlgorithmSearchCV
from json_tricks import dumps, loads
from scipy.stats import randint, uniform
from sklearn.base import BaseEstimator
from sklearn.datasets import load_iris
from sklearn.model_selection import (GridSearchCV, ParameterGrid,
                                     RandomizedSearchCV, train_test_split)
from sklearn.preprocessing import LabelEncoder

from cluster_strategies import (DummyClusterStrategy,
                                MostUncertainClusterStrategy,
                                RandomClusterStrategy,
                                RoundRobinClusterStrategy)
from dataStorage import DataStorage
from experiment_setup_lib import (ExperimentResult, Logger,
                                  classification_report_and_confusion_matrix,
                                  get_db, init_logging,
                                  load_and_prepare_X_and_Y, standard_config,
                                  store_pickle, store_result)
from sampling_strategies import (BoundaryPairSampler, CommitteeSampler,
                                 RandomSampler, UncertaintySampler)

standard_config = standard_config([])

init_logging(standard_config.output_dir)
db = get_db()

best_result = ExperimentResult.select().order_by(
    ExperimentResult.fit_score.desc()).limit(10)

for result in best_result:
    metrics = loads(result.metrics_per_al_cycle)

    amount_of_clusters = 0
    amount_of_certainties = 0
    for recommendation, query_length in zip(metrics['recommendation'],
                                            metrics['query_length']):
        if recommendation == 'U':
            amount_of_certainties += 1
        if recommendation == 'C':
            amount_of_clusters += 1

    print("{:>25} {:>25} {:4,d} {:4,d} {:2,d} {:5,d} {:6.2%} {:6.2%}".format(
        result.sampling, result.cluster, amount_of_clusters,
        amount_of_certainties, result.allow_recommendations_after_stop,
        result.amount_of_user_asked_queries, result.acc_test,
        result.fit_score))

# print for best run all the metrics from active_learner.py