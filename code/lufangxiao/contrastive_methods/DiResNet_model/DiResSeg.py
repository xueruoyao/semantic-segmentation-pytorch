import torch.nn as nn
from torch.nn import functional as F
import torch
import numpy as np
#from .FCN_8s import FCN
from .FCN_8s import FCN_res18a as FCN
#from .FCN_16s import FCN_res34a as FCN

BN_MOMENTUM = 0.01

def conv3x3(in_planes, out_planes, stride=1):
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride, padding=1, bias=False)


class FCN_Dec(nn.Module):
    def __init__(self, in_channels=3, num_classes=1, pretrained=True):
        super(FCN_Dec, self).__init__()
        self.FCN = FCN(in_channels, num_classes)
        
        self.Dec = nn.Sequential(nn.ConvTranspose2d(in_channels=64, out_channels=32, kernel_size=2, stride=2),
                                 nn.BatchNorm2d(32, momentum=BN_MOMENTUM), nn.ReLU(),
                                 nn.ConvTranspose2d(in_channels=32, out_channels=16, kernel_size=2, stride=2),
                                 nn.BatchNorm2d(16, momentum=BN_MOMENTUM), nn.ReLU(),
                                 nn.ConvTranspose2d(in_channels=16, out_channels=16, kernel_size=2, stride=2),
                                 nn.BatchNorm2d(16, momentum=BN_MOMENTUM), nn.ReLU())
                                                                
        self.classifier = nn.Conv2d(16, num_classes, kernel_size=1)
                
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                # 此处类似 resnet论文中的torch.nn.init.kaiming_uniform(), 但又不一样
                # n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                # m.weight.data.normal_(0, math.sqrt(2. / n))
                nn.init.kaiming_normal_(m.weight.data, nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()
        
    def forward(self, x):
        x_size = x.size()
        
        x = self.FCN.layer0(x)
        x = self.FCN.layer1(x)
        x = self.FCN.layer2(x)
        x = self.FCN.layer3(x)
        x = self.FCN.layer4(x)
        x = self.FCN.head(x)
                
        out = self.Dec(x)
        out = self.classifier(out)
        
        return out
