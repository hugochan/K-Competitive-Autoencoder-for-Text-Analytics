'''
Created on Nov, 2016

@author: hugo

'''
from __future__ import absolute_import
import argparse
from os import path
import numpy as np

from autoencoder.core.ae import AutoEncoder, load_model, save_model
# from autoencoder.core.deepae import DeepAutoEncoder
from autoencoder.preprocessing.preprocessing import load_corpus, doc2vec, vocab_weights
from autoencoder.utils.op_utils import vecnorm, corrupted_matrix
from autoencoder.utils.io_utils import dump_json


def train(args):
    corpus = load_corpus(args.input)
    n_vocab, docs = len(corpus['vocab']), corpus['docs']
    corpus.clear() # save memory

    X_docs = []
    for k in docs.keys():
        X_docs.append(vecnorm(doc2vec(docs[k], n_vocab), 'logmax1', 0))
        del docs[k]

    import pdb;pdb.set_trace()

    np.random.seed(0)
    np.random.shuffle(X_docs)
    # X_docs_noisy = corrupted_matrix(np.r_[X_docs], 0.1)

    n_val = args.n_val
    X_train = np.r_[X_docs[:-n_val]]
    X_val = np.r_[X_docs[-n_val:]]

    X_train_noisy = X_train
    X_val_noisy = X_val
    # X_train_noisy = X_docs_noisy[:-n_val]
    # X_val_noisy = X_docs_noisy[-n_val:]

    # model = DeepAutoEncoder
    model = AutoEncoder

    ae = model(n_vocab, args.n_dim, comp_topk=args.comp_topk, weights_file=args.load_weights)
    ae.fit([X_train_noisy, X_train], [X_val_noisy, X_val], nb_epoch=args.n_epoch, \
            batch_size=args.batch_size, feature_weights=None)

    if args.save_model:
        arch_file  = args.save_model + '.arch'
        weights_file  = args.save_model + '.weights'
        save_model(ae, arch_file, weights_file)
    print 'Saved model arch and weights file to %s and %s, respectively.' \
            % (arch_file, weights_file)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help='path to the input corpus file')
    parser.add_argument('-nd', '--n_dim', type=int, default=128, help='num of dimensions (default 128)')
    parser.add_argument('-ne', '--n_epoch', type=int, default=100, help='num of epoches (default 100)')
    parser.add_argument('-bs', '--batch_size', type=int, default=100, help='batch size (default 100)')
    parser.add_argument('-nv', '--n_val', type=int, default=1000, help='size of validation set (default 1000)')
    parser.add_argument('-ck', '--comp_topk', type=int, help='competitive topk')
    parser.add_argument('-lw', '--load_weights', type=str, help='path to the pretrained weights file')
    parser.add_argument('-sm', '--save_model', type=str, default='model', help='path to the output model')
    args = parser.parse_args()

    train(args)

if __name__ == '__main__':
    main()