import torch
from torch import nn


def argmax(vec):
    # return the argmax as a python int
    _, idx = torch.max(vec, 1)
    return idx.item()


def log_sum_exp(vec):
    max_score = vec[0, argmax(vec)]
    max_score_broadcast = max_score.view(1, -1).expand(1, vec.size()[1])
    return max_score + \
           torch.log(torch.sum(torch.exp(vec - max_score_broadcast)))


class LSTM_CRF(nn.Module):
    def __init__(self,
                 vocab_size: int, target_size: int, target_start_id: int, target_end_id: int,
                 word_embedding_dim: int, word_hidden_size: int, word_rnn_layers_count: int,
                 char_embedding_dim: int, char_hidden_size: int, char_rnn_layers_count: int):
        super().__init__()

        self.vocab_size = vocab_size

        self.target_size = target_size
        self.START_TAG_ID = target_start_id
        self.END_TAG_ID = target_end_id

        self.word_embedding_dim = word_embedding_dim
        self.word_hidden_size = word_hidden_size // 2 * 2
        self.word_rnn_layers_count = word_rnn_layers_count

        self.the_word_embedding = nn.Embedding(self.vocab_size, self.word_embedding_dim)
        self.the_word_lstm = nn.LSTM(
            self.word_embedding_dim,
            self.word_hidden_size // 2,
            num_layers=self.word_rnn_layers_count,
            bidirectional=True,
        )

        self.char_embedding_dim = char_embedding_dim
        self.char_hidden_size = char_hidden_size
        self.char_rnn_layers_count = char_rnn_layers_count

        self.hidden2tag = nn.Linear(self.word_hidden_size, self.target_size)

        # Matrix of transition parameters.  Entry i,j is the score of
        # transitioning *to* i *from* j.
        self.transitions = nn.Parameter(
            torch.randn(self.target_size, self.target_size))

        # These two statements enforce the constraint that we never transfer
        # to the start tag and we never transfer from the stop tag
        self.transitions.data[self.START_TAG_ID, :] = -10000
        self.transitions.data[:, self.END_TAG_ID] = -10000

    def _get_lstm_features(self, sentence, word_hidden=None):
        # 首先处理并计算
        word_embeds = self.the_word_embedding(sentence)  # [n, wembd_size]
        word_embeds = word_embeds.view(len(sentence), 1, -1)  # [n, wembd_size] -> [1, n * wembd_size]

        word_lstm_out, word_hidden = self.the_word_lstm(word_embeds, word_hidden)
        word_lstm_out = word_lstm_out.view(len(sentence), self.word_hidden_size)

        return self.hidden2tag(word_lstm_out)

    def _forward_alg(self, feats):
        # Do the forward algorithm to compute the partition function
        init_alphas = torch.full((1, self.target_size), -10000.)
        # START_TAG has all of the score.
        init_alphas[0][self.START_TAG_ID] = 0.

        # Wrap in a variable so that we will get automatic backprop
        forward_var = init_alphas

        # Iterate through the sentence
        for feat in feats:
            alphas_t = []  # The forward tensors at this timestep
            for next_tag in range(self.target_size):
                # broadcast the emission score: it is the same regardless of
                # the previous tag
                emit_score = feat[next_tag].view(
                    1, -1).expand(1, self.target_size)
                # the ith entry of trans_score is the score of transitioning to
                # next_tag from i
                trans_score = self.transitions[next_tag].view(1, -1)
                # The ith entry of next_tag_var is the value for the
                # edge (i -> next_tag) before we do log-sum-exp
                next_tag_var = forward_var + trans_score + emit_score
                # The forward variable for this tag is log-sum-exp of all the
                # scores.
                alphas_t.append(log_sum_exp(next_tag_var).view(1))
            forward_var = torch.cat(alphas_t).view(1, -1)
        terminal_var = forward_var + self.transitions[self.END_TAG_ID]
        alpha = log_sum_exp(terminal_var)
        return alpha

    def _score_sentence(self, feats, tags):
        # Gives the score of a provided tag sequence
        score = torch.zeros(1)
        tags = torch.cat([torch.LongTensor([self.START_TAG_ID]), tags])
        for i, feat in enumerate(feats):
            score = score + \
                    self.transitions[tags[i + 1], tags[i]] + feat[tags[i + 1]]
        score = score + self.transitions[self.END_TAG_ID, tags[-1]]
        return score

    def _viterbi_decode(self, feats):
        backpointers = []

        # Initialize the viterbi variables in log space
        init_vvars = torch.full((1, self.target_size), -10000.)
        init_vvars[0][self.START_TAG_ID] = 0

        # forward_var at step i holds the viterbi variables for step i-1
        forward_var = init_vvars
        for feat in feats:
            bptrs_t = []  # holds the backpointers for this step
            viterbivars_t = []  # holds the viterbi variables for this step

            for next_tag in range(self.target_size):
                # next_tag_var[i] holds the viterbi variable for tag i at the
                # previous step, plus the score of transitioning
                # from tag i to next_tag.
                # We don't include the emission scores here because the max
                # does not depend on them (we add them in below)
                next_tag_var = forward_var + self.transitions[next_tag]
                best_tag_id = argmax(next_tag_var)
                bptrs_t.append(best_tag_id)
                viterbivars_t.append(next_tag_var[0][best_tag_id].view(1))
            # Now add in the emission scores, and assign forward_var to the set
            # of viterbi variables we just computed
            forward_var = (torch.cat(viterbivars_t) + feat).view(1, -1)
            backpointers.append(bptrs_t)

        # Transition to STOP_TAG
        terminal_var = forward_var + self.transitions[self.END_TAG_ID]
        best_tag_id = argmax(terminal_var)
        path_score = terminal_var[0][best_tag_id]

        # Follow the back pointers to decode the best path.
        best_path = [best_tag_id]
        for bptrs_t in reversed(backpointers):
            best_tag_id = bptrs_t[best_tag_id]
            best_path.append(best_tag_id)
        # Pop off the start tag (we dont want to return that to the caller)
        start = best_path.pop()
        assert start == self.START_TAG_ID  # Sanity check
        best_path.reverse()
        return path_score, best_path

    def neg_log_likelihood(self, sentence, tags, word_hidden=None):
        feats = self._get_lstm_features(sentence, word_hidden)
        forward_score = self._forward_alg(feats)
        gold_score = self._score_sentence(feats, tags)
        return forward_score - gold_score

    def forward(self, sentence, word_hidden=None):
        lstm_feats = self._get_lstm_features(sentence, word_hidden)

        # Find the best path, given the features.
        score, tag_seq = self._viterbi_decode(lstm_feats)
        return score, tag_seq
