from torch.utils.data import Dataset
from transformers import BertTokenizer
import torch

class AmazonReviewsDataset(Dataset):
    def __init__(self, df, maxlen):
        self.df = df
        # A reset reindexes from 1 to len(df), the shuffled df frames are sparse.
        self.df.reset_index(drop=True, inplace=True)
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.maxlen = maxlen

    def __len__(self):
        return(len(self.df))

    def __getitem__(self, index):
        review = self.df.loc[index, 'Text']

        # Classes start from 0.
        label = int(self.df.loc[index, 'Score']) - 1

        # Use BERT tokenizer since it needs to be able to match the tokens to the pre trained words.
        tokens = self.tokenizer.tokenize(review)

        # BERT inputs typically start with a '[CLS]' tag and end with a '[SEP]' tag. For
        tokens = ['[CLS]'] + tokens + ['[SEP]']

        if len(tokens) < self.maxlen:
            # Add the ['PAD'] token
            tokens = tokens + ['[PAD]' for item in range(self.maxlen-len(tokens))]
        else:
            # Truncate the tokens at maxLen - 1 and add a '[SEP]' tag.
            tokens = tokens[:self.maxlen-1] + ['[SEP]']

        # BERT tokenizer converts the string tokens to their respective IDs.
        token_ids = self.tokenizer.convert_tokens_to_ids(tokens)

        # Converting to pytorch tensors.
        tokens_ids_tensor = torch.tensor(token_ids)

        # Masks place a 1 if token != PAD else a 0.
        attn_mask = (tokens_ids_tensor != 0).long()

        return tokens_ids_tensor, attn_mask, label
