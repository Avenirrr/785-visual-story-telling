import torch
FEATURE_EXTRACTOR = "resnet152"
FC7_SIZE = 4096
HIDDEN_SIZE = 1024
EMBEDDING_SIZE = 400
NUM_PICS = 5
NUM_SENTS = 5
BATCH_SIZE = 2
MAX_SENT_LEN = 60
MAX_STORY_LEN = 200
PRINT_LOSS = 10
INPUT_DROPOUT = 0.2
OUTPUT_DROPOUT = 0.2
WEIGHT_DROP = 0.5
BIDIRECTIONAL_ENCODER = True
BIDIRECTIONAL_DECODER = False 
NUM_LAYERS_ENCODER = 3
NUM_LAYERS_DECODER = 3
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'