from torch.utils.data import Dataset
import torch
import torch.nn as nn
import os
import pandas as pd
import numpy as np
import random
import nibabel as nib
from torch.utils.data import DataLoader
import torch.nn.functional as F

def load_image(image_path, mean, std, threshold = [-1200, 600]):
    image = nib.load(image_path).get_fdata()#.astype(np.int32)
    np.clip(image,threshold[0],threshold[1],out=image)
    np.subtract(image, mean, out = image)
    np.divide(image, std, out = image)
    image = image.transpose(2, 1, 0)
    return image

def load_image_norm(image_path, threshold = [-1200, 600]):
    image = nib.load(image_path).get_fdata()#.astype(np.int32)
    # np.subtract(image, mean, out = image)
    # np.divide(image, std, out = image)
    np.clip(image,threshold[0],threshold[1],out=image)
    image = (image-threshold[0])/(threshold[1] - threshold[0])
    image = image.transpose(2, 1, 0)
    return image

class TrainDataset(Dataset):
    def __init__(self, train_data_dir, train_df_csv, labels_train_df_csv):
        self.data_dir = train_data_dir
        train_df = pd.read_csv(train_df_csv)
        self.names_train = train_df["name"]#["B19_PA11_SE1"]#
        self.labels_train_df = pd.read_csv(labels_train_df_csv, index_col=0)
        self.mean = -604.2288900583559
        self.std = 489.42172740885655
    def __getitem__(self, item):
        # random.seed(0)
        margin =8
        name_train = self.names_train[item]
        label_train = self.labels_train_df.at[name_train, "four_label"]
        path_train = self.data_dir + name_train + ".nii.gz"
        # image_train = nib.load(path_train).get_fdata().astype(np.int32).transpose(2, 1, 0)
        image_train = load_image(path_train, self.mean, self.std)
        z_train, h_train, w_train = image_train.shape
        image_train=torch.from_numpy(image_train).float()
        index_list=[]
        if z_train<=80:
            # start=random.randrange(0,z_train-15)
            # for i in range(margin * 2):
            #     index_list.append(start+i*1)
            # start=random.randrange(0,z_test-15)
            if z_train <= 16:
                start = 0
            else:
                start = random.randrange(0,z_train-16)
            for i in range(margin * 2):
                index_list.append(start+i*1)
        elif z_train<=160:
            start=random.randrange(10,z_train-60)
            for i in range(margin * 2):
                index_list.append(start+i*2)#5)
        else:
            start=random.randrange(20,z_train-130)
            for i in range(margin * 2):
                index_list.append(start+i*5)#10)

        image_train_crop=[]
        for index in index_list:
            # print(z_train)
            if z_train < margin*2:
                left_pad = (margin * 2 - z_train)//2
                right_pad = margin * 2 - left_pad - z_train
                pad = (0, 0, 0, 0, left_pad, right_pad)
                image_train = F.pad(image_train, pad, "constant")
            image_train_crop.append(image_train[index,:,:])
        image_train_crop=torch.stack(image_train_crop,0).float()
        #image_train_crop = image_train[(z_train//2 - margin) : (z_train//2 + margin), :, :]
        return image_train_crop, label_train, name_train


    def __len__(self):
        return len(self.names_train)


class TestDataset(Dataset):
    def __init__(self, test_data_dir, test_df_csv, labels_test_df_csv):
        self.data_dir = test_data_dir
        test_df = pd.read_csv(test_df_csv)
        self.names_test = test_df["name"]#["B19_PA11_SE1"]#
        self.labels_test_df = pd.read_csv(labels_test_df_csv, index_col=0)
        self.mean = -604.2288900583559
        self.std = 489.42172740885655


    def __getitem__(self, item):
     #   random.seed(0)
        margin = 8
        name_test = self.names_test[item]
        label_test = self.labels_test_df.at[name_test, "four_label"]
        patient_id = self.labels_test_df.at[name_test, "patient_id"]
        path_test = self.data_dir + name_test + ".nii.gz"
        # image_test = nib.load(path_test).get_fdata().astype(np.int32).transpose(2, 1, 0)
        image_test = load_image(path_test, self.mean, self.std)
        #image_test = load_image_norm(path_test)
        z_test, h_test, w_test = image_test.shape
        image_test=torch.from_numpy(image_test).float()
        index_list=[]
        if z_test<=80:
            # start=random.randrange(0,z_test-15)
            # for i in range(margin * 2):
            #     index_list.append(start+i*1)
            # start=random.randrange(0,z_test-15)
            if z_test <= margin*2:
                start = 0
            else:
                start = random.randrange(0,z_test-margin*2)
            for i in range(margin * 2):
                index_list.append(start+i*1)
        elif z_test<=160:
            start=random.randrange(10,z_test-60)
            for i in range(margin * 2):
                index_list.append(start+i*2)#5)
        else:
            start=random.randrange(30,z_test-120)
            for i in range(margin * 2):
                index_list.append(start+i*5)#10)

        image_test_crop=[]
        for index in index_list:
            # print(z_test)
            if z_test < margin*2:
                left_pad = (margin * 2 - z_test)//2
                right_pad = margin * 2 - left_pad - z_test
                pad = (0, 0, 0, 0, left_pad, right_pad)
                image_test = F.pad(image_test, pad, "constant")
            image_test_crop.append(image_test[index,:,:])
        image_test_crop=torch.stack(image_test_crop,0).float()
        #image_test_crop = image_test[(z_test//2 - margin) : (z_test//2 + margin), :, :]
        return image_test_crop, label_test, name_test, patient_id


    def __len__(self):
        return len(self.names_test)
