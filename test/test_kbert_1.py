import torch
import torch.nn as nn
import torch.optim as optim
from cogktr import *
from cogktr.utils.general_utils import init_cogktr
from cogktr.utils.constant.kbert_constants.constants import *
from cogktr.data.processor.sst2_processors.sst2_for_kbert_processor import *
from cogktr.models.kbert_model import KBertModelBuilder
from cogktr.modules.layers.optimizers import BertAdam
from cogktr.models.kbert_model_1 import KBertForSequenceClassification

# initiate
device, output_path = init_cogktr(
    device_id=0,
    output_path="/home/chenyuheng/zhouyuyang/CogKTR/datapath/text_classification/SST_2/experimental_result",
    folder_tag="simple_test",
)
# device = torch.device("cpu")

# Load the data
reader = Sst2Reader(raw_data_path="/home/chenyuheng/zhouyuyang/CogKTR/datapath/text_classification/SST_2/raw_data")
train_data, dev_data, test_data = reader.read_all()
vocab = reader.read_vocab()

# processor
processor = Sst2ForKbertProcessor(plm="bert-base-uncased",
                                      spo_file_paths=["/home/chenyuheng/zhouyuyang/CogKTR/datapath/knowledge_graph/wikidata/wikidata.spo"],
                                      max_token_len=256)

train_dataset = processor.process_train(train_data)
dev_dataset = processor.process_dev(dev_data)
test_dataset = processor.process_test(test_data)

model = KBertForSequenceClassification(plm="bert-base-uncased", vocab=vocab)
metric = BaseClassificationMetric(mode="binary")
loss = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.00001)

trainer = Trainer(model,
                  train_dataset,
                  dev_data=dev_dataset,
                  n_epochs=20,
                  batch_size=50,
                  loss=loss,
                  optimizer=optimizer,
                  scheduler=None,
                  metrics=metric,
                  train_sampler=None,
                  dev_sampler=None,
                  drop_last=False,
                  gradient_accumulation_steps=1,
                  num_workers=5,
                  print_every=None,
                  scheduler_steps=None,
                  validate_steps=100,
                  save_steps=100,
                  output_path=output_path,
                  grad_norm=1,
                  use_tqdm=True,
                  device=device,
                  callbacks=None,
                  metric_key=None,
                  fp16=False,
                  fp16_opt_level='O1',
                  collate_fn=train_dataset.to_dict,
                  dev_collate_fn=dev_dataset.to_dict,
                  )
trainer.train()
print("end")