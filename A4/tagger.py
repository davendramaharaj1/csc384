# The tagger.py starter code for CSC384 A4.

import os
import sys

import numpy as np
from collections import Counter

UNIVERSAL_TAGS = [
    "VERB",
    "NOUN",
    "PRON",
    "ADJ",
    "ADV",
    "ADP",
    "CONJ",
    "DET",
    "NUM",
    "PRT",
    "X",
    ".",
]

N_tags = len(UNIVERSAL_TAGS)

def read_data_train(path):
    return [tuple(line.split(' : ')) for line in open(path, 'r').read().split('\n')[:-1]]

def read_data_test(path):
    return open(path, 'r').read().split('\n')[:-1]

def read_data_ind(path):
    return [int(line) for line in open(path, 'r').read().split('\n')[:-1]]

def write_results(path, results):
    with open(path, 'w') as f:
        f.write('\n'.join(results))

def train_HMM(train_file_name):
    """
    Estimate HMM parameters from the provided training data.

    Input: Name of the training files. Two files are provided to you:
            - file_name.txt: Each line contains a pair of word and its Part-of-Speech (POS) tag
            - fila_name.ind: The i'th line contains an integer denoting the starting index of the i'th sentence in the text-POS data above

    Output: Three pieces of HMM parameters stored in LOG PROBABILITIES :
 
            - prior:        - An array of size N_tags
                            - Each entry corresponds to the prior log probability of seeing the i'th tag in UNIVERSAL_TAGS at the beginning of a sequence
                            - i.e. prior[i] = log P(tag_i)

            - transition:   - A 2D-array of size (N_tags, N_tags)
                            - The (i,j)'th entry stores the log probablity of seeing the j'th tag given it is a transition coming from the i'th tag in UNIVERSAL_TAGS
                            - i.e. transition[i, j] = log P(tag_j|tag_i)

            - emission:     - A dictionary type containing tuples of (str, str) as keys
                            - Each key in the dictionary refers to a (TAG, WORD) pair
                            - The TAG must be an element of UNIVERSAL_TAGS, however the WORD can be anything that appears in the training data
                            - The value corresponding to the (TAG, WORD) key pair is the log probability of observing WORD given a TAG
                            - i.e. emission[(tag, word)] = log P(word|tag)
                            - If a particular (TAG, WORD) pair has never appeared in the training data, then the key (TAG, WORD) should not exist.

    Hints: 1. Think about what should be done when you encounter those unseen emission entries during deccoding.
           2. You may find Python's builtin Counter object to be particularly useful 
    """

    pos_data = read_data_train(train_file_name+'.txt')
    sent_inds = read_data_ind(train_file_name+'.ind')

    ####################
    # STUDENT CODE HERE
    ####################

    #################### Prior Probabilities using Unigram ####################
    prior = list()

    # get the tags of the 1st word for every sequence
    tags = [pos_data[word][1] for word in sent_inds]
    # create a frequency table for the tags of first words
    tag_histogram = Counter(tags)
    # order the entries from the histogram according to Universal Tags
    prior_frequency = [tag_histogram[tag_val] for tag_val in UNIVERSAL_TAGS]
    # get the total
    all_words = sum(tag_histogram.values())
    # get the log probabilities per tag
    prior = np.log([num/all_words for num in prior_frequency])

    #################### Transition using Bigram ####################
    '''
    P(t2 | t1) = num of bigrams = t1 t2 / num of bigrams beginning with t1
    '''
    # create a 2d array 
    transition = [[0 for x in range(N_tags)] for y in range(N_tags)]

    # get a list of bigrams of tags
    bigrams = list() # list of tuples (t1, t2)
    first_word = list() # list of first words that start each bigram 

    for idx in range(len(sent_inds)):
        sentence = list()
        # if we reached the last sentence
        if idx == len(sent_inds) - 1:
            sentence = pos_data[sent_inds[idx]:]
        else:
            sentence = pos_data[sent_inds[idx]:sent_inds[idx+1]]
        
        # we only consider the tags, not the words
        sentence = [word[1] for word in sentence]

        # get the bigrams and initial word per bigram
        for t_val in range(len(sentence) - 1):
            bigrams.append((sentence[t_val], sentence[t_val+1]))
            first_word.append(sentence[t_val])
    
    # create histograms of the bigrams and first word per bigram to calculate probabilties
    bigram_table = Counter(bigrams)
    first_table = Counter(first_word)

    # populate transition table
    for i in range(N_tags):
        _tag_i = UNIVERSAL_TAGS[i]
        for j in range(N_tags):
            _tag_j = UNIVERSAL_TAGS[j]
            transition[i][j] = np.true_divide(bigram_table[(_tag_i, _tag_j)], first_table[_tag_i])
    
    transition = np.log(transition)

    #################### Emission using Naive Tagger Estimation ####################
    emission = dict()

    # get the tag count and tag, word pair
    tag_list, tag_word = [word[1] for word in pos_data], [word[::-1] for word in pos_data]

    # get the frequency for each tag count and token pair
    tag_freq, tag_word_freq = Counter(tag_list), Counter(tag_word)

    for pair, freq in tag_word_freq.items():
        emission[pair] = np.log(np.true_divide(freq, tag_freq[pair[0]]))

    return prior, transition, emission
    

def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """

    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')

    results = list()

    ####################
    # STUDENT CODE HERE
    ####################
    small_prob = np.log([1e-10])[0]

    # iterate through every sentence
    for idx in range(len(sent_inds)):

        # get the sentence
        sentence = list()

        # if we've reached the last sentence
        if idx == len(sent_inds) - 1:
            sentence = pos_data[sent_inds[idx]:]
        else:
            sentence = pos_data[sent_inds[idx]:sent_inds[idx+1]]
        
        '''
        From lecture notes:
        S: States ---> in this case, tags to deduce (we want to predict the states)
        O: Observations ---> in this case, words in sentence
        '''
        S = N_tags
        O = len(sentence)

        # probability trellis filled with small values instead of zero
        value_trellis = np.full((S, O), small_prob)
        # path trellis to track argmax
        path_trellis = [[[] for obs in range(O)] for state in range(S)]

        # Determine trellis values for 1st column 
        for state in range(S):
            # if (tag, word) doesn't exist, put a small probability
            value_trellis[state, 0] = prior[state] + emission.get((UNIVERSAL_TAGS[state], sentence[0]), small_prob)
            path_trellis[state, 0] = [state]
        
        # For S2 - S1, find the most likely prior for the current state
        for obs in range(1, O):
            # we need the previous probabilities
            previous_val = value_trellis[:, obs - 1]
            for state in range(S):
                # retrieve transition probabilities until current state
                curr_transition = transition[:, state]

                # retrieve emission probabilities of obs given some tag
                emission_pair = np.array([emission.get((UNIVERSAL_TAGS[state], sentence[obs]), small_prob)] * S)

                # combine prev_value with transition and emission
                combined = np.sum([previous_val, curr_transition, emission_pair], axis=0)

                # find the indices yielding max
                max = np.argmax(combined)

                value_trellis[state, obs] = combined[max]
                path_trellis[state][obs] = path_trellis[max][obs - 1] + [state]
        
        # get the indices of the tags on the max path
        tag_idx = path_trellis[np.argmax(value_trellis[:, O-1])][O-1]

        # get the tags
        res_tags = [UNIVERSAL_TAGS[tval] for tval in tag_idx]

        # append to results
        results += res_tags

    write_results(test_file_name+'.pred', results)

if __name__ == '__main__':
    # Run the tagger function.
    print("Starting the tagging process.")

    # Tagger expects the input call: "python3 tagger.py -d <training file> -t <test file>"
    # E.g. python3 tagger.py -d data/train-public -t data/test-public-small
    parameters = sys.argv
    train_file_name = parameters[parameters.index("-d")+1]
    test_file_name = parameters[parameters.index("-t")+1]

    # Start the training and tagging operation.
    tag (train_file_name, test_file_name)
