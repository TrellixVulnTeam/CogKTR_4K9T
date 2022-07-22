from cogktr.data.datable import DataTable
from cogktr.data.datableset import DataTableSet
from transformers import BertTokenizer
from tqdm import tqdm
import transformers
from cogktr.data.processor.base_processor import BaseProcessor

transformers.logging.set_verbosity_error()  # set transformers logging level


class Sst5Processor(BaseProcessor):
    def __init__(self, plm, max_token_len, vocab):
        super().__init__()
        self.plm = plm
        self.max_token_len = max_token_len
        self.vocab = vocab
        self.tokenizer = BertTokenizer.from_pretrained(plm)

    def _process(self, data):
        datable = DataTable()
        print("Processing data...")
        for sentence, label in tqdm(zip(data['sentence'], data['label']), total=len(data['sentence'])):
            tokenized_result = self.tokenizer.encode_plus(text=sentence,
                                                          truncation=True,
                                                          padding="max_length",
                                                          add_special_tokens=True,
                                                          max_length=self.max_token_len)
            datable("input_ids", tokenized_result["input_ids"])
            datable("attention_mask", tokenized_result["attention_mask"])
            datable("label", self.vocab["label_vocab"].label2id(label))
        return DataTableSet(datable)

    def process_train(self, data):
        return self._process(data)

    def process_dev(self, data):
        return self._process(data)

    def process_test(self, data):
        return self._process(data)


if __name__ == "__main__":
    from cogktr.data.reader.sst5_reader import Sst5Reader

    reader = Sst5Reader(raw_data_path="/data/mentianyi/code/CogKTR/datapath/text_classification/SST_5/raw_data")
    train_data, dev_data, test_data = reader.read_all()
    vocab = reader.read_vocab()

    processor = Sst5Processor(plm="bert-base-cased", max_token_len=128, vocab=vocab)
    train_dataset = processor.process_train(train_data)
    dev_dataset = processor.process_dev(dev_data)
    test_dataset = processor.process_test(test_data)
    print("end")
