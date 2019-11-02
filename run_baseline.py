from vocab import *
import sys
# sys.path.insert(0, 'vist_api/vist')
from vist_api.vist import *
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import torchvision
import os.path as osp
import torch
import pickle
from baseline_model import *
from hyperparams import *
import os

vocab_save_path = "vocab.pt"
vist_annotations_dir = '/Users/xiangtic/vist/'
images_dir = '/Users/xiangtic/vist/images/'
sis_train = Story_in_Sequence(images_dir + "toy", vist_annotations_dir)
# sis_val = Story_in_Sequence(images_dir+"val", vist_annotations_dir)
# sis_test = Story_in_Sequence(images_dir+"test", vist_annotations_dir)

cuda = True
cuda = cuda and torch.cuda.is_available()
device = torch.device("cuda" if cuda else "cpu")

# build/read vocabulary
if not osp.exists(vocab_save_path):
    corpus = []
    for story in sis_train.Stories:
        sent_ids = sis_train.Stories[story]['sent_ids']
        for sent_id in sent_ids:
            corpus.append(sis_train.Sents[sent_id]['text'])
    vocab = Vocabulary(corpus, freq_cutoff=3)
    vocab.build()
    pickle.dump(vocab, open(vocab_save_path, 'wb'))
else:
    vocab = pickle.load(open(vocab_save_path, 'rb'))


# build dataloader
class StoryDataset(Dataset):
    def __init__(self, sis, vocab):
        self.sis = sis
        self.story_indices = list(self.sis.Stories.keys())
        self.vocab = vocab

    def __len__(self):
        return len(self.sis.Stories)

    @staticmethod
    def read_image(path):
        img = Image.open(path)
        img = torchvision.transforms.Resize((224, 224))(img)
        img = torchvision.transforms.ToTensor()(img)
        return img

    def __getitem__(self, idx):
        story_id = self.story_indices[idx]
        story = self.sis.Stories[story_id]
        sent_ids = story['sent_ids']
        img_ids = story['img_ids']
        imgs = []
        for i, img_id in enumerate(img_ids):
            img_file = osp.join(self.sis.images_dir, img_id + '.jpg')
            img_tensor = self.read_image(img_file)
            imgs.append(img_tensor)
        imgs = torch.stack(imgs)

        sents = []
        for sent_id in sent_ids:
            sent_tensor = self.vocab.sent2vec("<s> " + self.sis.Sents[sent_id]["text"] + " </s>")
            container = torch.zeros(MAX_SENT_LEN).fill_(self.vocab["<pad>"])
            container[:len(sent_tensor)] = sent_tensor
            sents.append(container)
            # print(container)
        sents = torch.stack(sents)
        return imgs, sents


train_story_set = StoryDataset(sis_train, vocab)
# val_story_set = StoryDataset(sis_val, vocab)
# test_story_set = StoryDataset(sis_test, vocab)


train_loader = DataLoader(train_story_set, shuffle=False, batch_size=BATCH_SIZE)
# imgs of shape [BS, 5, 3, 224, 224]
# sents BS * 5  * MAX_LEN

# for batch, (imgs, sents) in enumerate(train_loader):
#     print(imgs.size())
#     print(sents.size())
#     raise 123

baseline_model = BaselineModel(vocab)
optimizer = torch.optim.Adam(baseline_model.parameters(), lr=0.01)


def train(epochs, model, train_dataloader):
    init_hidden = torch.rand(1, BATCH_SIZE, HIDDEN_SIZE, device=device)
    model.train()
    for epoch in range(epochs):
        avg_loss = 0
        for batch_num, (images, sents) in enumerate(train_dataloader):
            optimizer.zero_grad()
            loss = -model(images, sents, init_hidden)
            loss.backward()
            optimizer.step()
            avg_loss += loss.item()
            print(loss.item())

            if batch_num % 50 == 49:
                print('Epoch: {}\tBatch: {}\tAvg-Loss: {:.4f}'.format(epoch + 1, batch_num + 1, avg_loss / 50))
                avg_loss = 0.0

            # torch.cuda.empty_cache()

        # torch.save(model.state_dict(), model_path + "/"+ str(epoch) +".pt")


train(1, baseline_model, train_loader)
