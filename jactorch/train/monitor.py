# -*- coding: utf-8 -*-
# File   : monitor.py
# Author : Jiayuan Mao
# Email  : maojiayuan@gmail.com
# Date   : 12/04/2018
#
# This file is part of Jacinle.

import torch.nn.functional as F
from jactorch.utils.meta import as_tensor, as_float

__all__ = [
    'binary_classification_accuracy',
    'regression_accuracy',
    'monitor_param_saturation',
    'monitor_param_rms',
    'monitor_param_gradrms', 'monitor_param_gradrms_ratio'
]


def binary_classification_accuracy(pred, label, name='', saturation=True):
    if name != '':
        name = '/' + name
    prefix = 'accuracy' + name
    pred = as_tensor(pred).view(-1)  # Binary accuracy
    label = as_tensor(label).view(-1)
    acc = label.float().eq((pred > 0.5).float())
    if saturation:
        sat = 1 - (pred - (pred > 0.5).float()).abs()
        return {
            prefix: as_float(acc.float().mean()),
            prefix + '/saturation/mean': as_float(sat.mean()),
            prefix + '/saturation/min': as_float(sat.min())
        }
    return {prefix: as_float(acc.float().mean())}


def regression_accuracy(pred, label, name=''):
    if name != '':
        name = '/' + name
    prefix = 'accuracy' + name
    pred = as_tensor(pred).view(-1)  # Binary accuracy
    label = as_tensor(label).view(-1)
    diff = pred - label
    return {
        prefix + '/l1': as_float(diff.abs().mean()),
        prefix + '/l2': as_float(0.5 * diff.pow(2).mean())
    }


def _rms(p):
    return as_float((as_tensor(p) ** 2).mean() ** 0.5)


def monitor_param_saturation(model):
    monitors = {}
    for name, p in model.named_parameters():
        p = F.sigmoid(p)
        sat = 1 - (p - (p > 0.5).float()).abs()
        monitors['sat/' + name] = sat
    return monitors


def monitor_param_rms(model):
    monitors = {}
    for name, p in model.named_parameters():
        monitors['param/rms/' + name] = _rms(p)
    return monitors


def monitor_param_gradrms(model):
    monitors = {}
    for name, p in model.named_parameters():
        if p.grad is not None:
            monitors['param/gradrms/' + name] = _rms(p.grad)
    return monitors


def monitor_param_gradrms_ratio(model):
    monitors = {}
    for name, p in model.named_parameters():
        if p.grad is not None:
            monitors['param/gradrmsratio/' + name] = _rms(p.grad) / max(_rms(p), 1e-8)
    return monitors
