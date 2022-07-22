from cogktr.data.datable import DataTable
from tqdm import tqdm
from cogktr.enhancers.world_enhancer import WorldEnhancer
from transformers import BertTokenizer
from cogktr.data.processor.base_processor import BaseProcessor
import numpy as np
from cogktr.data.datableset import DataTableSet


class Sst5ForKtattProcessor(BaseProcessor):
    def __init__(self, plm, max_token_len, vocab):
        super().__init__()
        self.plm = plm
        self.max_token_len = max_token_len
        self.vocab = vocab
        self.tokenizer = BertTokenizer.from_pretrained(plm)

    def _process(self, data, enhanced_dict=None):
        datable = DataTable()
        print("Processing data...")

        for sentence, label in tqdm(zip(data['sentence'], data['label']), total=len(data['sentence'])):
            # token_ids = self.tokenizer.encode(text=enhanced_dict[sentence]['words'],
            #                                   truncation=True,
            #                                   padding="max_length",
            #                                   add_special_tokens=False,
            #                                   max_length=self.max_token_len)
            token_ids = self.tokenizer.encode(enhanced_dict[sentence]['words'])
            attention_mask = np.zeros((self.max_token_len, self.max_token_len))
            lst_pos = len(token_ids)
            attention_mask[0:lst_pos, 0:lst_pos] = 1

            entities = enhanced_dict[sentence]['entities']
            for entity in entities:
                if isinstance(entity['desc'], str):
                    entity_desc_token_ids = self.tokenizer.encode(entity['desc'], add_special_tokens=False)
                    curr_lst_pos = min(lst_pos + len(entity_desc_token_ids), self.max_token_len)
                    attention_mask[lst_pos:curr_lst_pos, lst_pos:curr_lst_pos] = 1
                    attention_mask[entity['start'] + 1:entity['end'] + 1, lst_pos:curr_lst_pos] = 1
                    attention_mask[lst_pos:curr_lst_pos, entity['start'] + 1:entity['end'] + 1] = 1
                    lst_pos = curr_lst_pos
                    if lst_pos <= self.max_token_len:
                        token_ids = token_ids + entity_desc_token_ids
                    else:
                        token_ids = (token_ids + entity_desc_token_ids)[0:self.max_token_len]
                        break
            if lst_pos < self.max_token_len:
                token_ids = token_ids + [0] * (self.max_token_len - lst_pos)

            token_ids = token_ids[:self.max_token_len]

            datable("input_ids", token_ids)
            datable("attention_mask", attention_mask)
            datable("label", self.vocab["label_vocab"].label2id(label))
        return DataTableSet(datable)

    def process_train(self, data, enhanced_dict=None):
        return self._process(data, enhanced_dict)

    def process_dev(self, data, enhanced_dict=None):
        return self._process(data, enhanced_dict)

    def process_test(self, data, enhanced_dict=None):
        datable = DataTable()
        print("Processing data...")

        for sentence in tqdm(data['sentence'], total=len(data['sentence'])):
            token_ids = self.tokenizer.encode(enhanced_dict[sentence]['words'])
            attention_mask = np.zeros((self.max_token_len, self.max_token_len))
            lst_pos = len(token_ids)
            attention_mask[0:lst_pos, 0:lst_pos] = 1

            entities = enhanced_dict[sentence]['entities']
            for entity in entities:
                if isinstance(entity['desc'], str):
                    entity_desc_token_ids = self.tokenizer.encode(entity['desc'], add_special_tokens=False)
                    curr_lst_pos = min(lst_pos + len(entity_desc_token_ids), self.max_token_len)
                    attention_mask[lst_pos:curr_lst_pos, lst_pos:curr_lst_pos] = 1
                    attention_mask[entity['start'] + 1:entity['end'] + 1, lst_pos:curr_lst_pos] = 1
                    attention_mask[lst_pos:curr_lst_pos, entity['start'] + 1:entity['end'] + 1] = 1
                    lst_pos = curr_lst_pos
                    if lst_pos <= self.max_token_len:
                        token_ids = token_ids + entity_desc_token_ids
                    else:
                        token_ids = (token_ids + entity_desc_token_ids)[0:self.max_token_len]
                        break
            if lst_pos < self.max_token_len:
                token_ids = token_ids + [0] * (self.max_token_len - lst_pos)

            datable("input_ids", token_ids)
            datable("attention_mask", attention_mask)
        return DataTableSet(datable)


if __name__ == "__main__":
    from cogktr.data.reader.sst5_reader import Sst5Reader

    reader = Sst5Reader(raw_data_path="/data/mentianyi/code/CogKTR/datapath/text_classification/SST_5/raw_data")
    train_data, dev_data, test_data = reader.read_all()
    vocab = reader.read_vocab()

    enhancer = WorldEnhancer(knowledge_graph_path="/data/mentianyi/code/CogKTR/datapath/knowledge_graph",
                             cache_path="/data/mentianyi/code/CogKTR/datapath/text_classification/SST_5/enhanced_data",
                             cache_file="world_data",
                             reprocess=False,
                             load_entity_desc=True,
                             load_entity_embedding=False,
                             load_entity_kg=False)
    enhanced_dev_dict = enhancer.enhance_dev(datable=dev_data,
                                             enhanced_key_1="sentence",
                                             return_entity_desc=True,
                                             return_entity_embedding=False,
                                             return_entity_kg=False)

    processor = Sst5ForKtattProcessor(plm="bert-base-cased", max_token_len=128, vocab=vocab)
    dev_dataset = processor.process_dev(data=dev_data, enhanced_dict=enhanced_dev_dict)
    print("end")
