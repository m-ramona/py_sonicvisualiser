# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 David Doukhan <david.doukhan@gmail.com>

# This file is part of py_sonicvisualiser.

# py_sonicvisualiser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

# py_sonicvisualiser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with TimeSide.  If not, see <http://www.gnu.org/licenses/>.

# Author: David Doukhan <david.doukhan@gmail.com>

"""
This class is allows the storage of large continuous dataset
in xml.dom.minidom documents
"""

import xml.dom.minidom
import collections
import numpy as np


class SVDataset(xml.dom.minidom.Text):
    """
    This class is aimed at storing large datasets in minidom documents
    datasets are stored as iterable structure (lists, numpy arrays, ...)
    This data is converted to sonic visualiser point nodes at writing time
    This allows to avoid the storage of very large xml trees in RAM,
    and avoid swap
    """

    def __init__(self, domdoc, datasetid, samplerate):
        self.datasetid = datasetid
        self.frames = []
        self.values = []
        self.labels = []
        self.label2int = dict()
        self.int2label = dict()
        self.ownerDocument = domdoc
        self.samplerate = samplerate
        self.parentNode = None
        self.tagName = 'dataset'

    def set_data_from_iterable(self, frames, values=None, labels=None):
        """
        Initialize a dataset structure from iterable parameters

        :param frames: The temporal indices of the dataset
        :param values: The values of the dataset
        :type frames: iterable
        :type values: iterable
        """
        if not isinstance(frames, collections.Iterable):
            raise TypeError("frames must be an iterable")
        if values is not None:
            if not isinstance(values, collections.Iterable):
                raise TypeError("values must be an iterable")
            assert(len(frames) == len(values))

        self.frames = list(frames)
        self.values = values
        if labels is None:
            self.label2int[''] = 0
            self.int2label[0] = ''
            self.labels = [0 for i in range(len(self.frames))]
        else:
            if not isinstance(labels, collections.Iterable):
                raise TypeError("labels must be an iterable")
            for l in labels:
                if l not in self.label2int:
                    self.label2int[l] = len(self.label2int)
                    self.int2label[len(self.int2label)] = l
                self.labels.append(self.label2int[l])

    def append_xml_point(self, attrs):
        self.frames.append(int(attrs.getValue('frame')))
        if self.values is not None:
            self.values.append(float(attrs.getValue('value')))
        l = attrs.getValue('label')
        if l not in self.label2int:
            self.label2int[l] = len(self.label2int)
            self.int2label[len(self.int2label)] = l
        self.labels.append(self.label2int[l])

    def get_instants(self):
        return np.divide(self.frames,self.samplerate)

    def get_labels(self):
        if self.labels is None:
            return None
        return list(map(lambda x: self.int2label[x], self.labels))

    def writexml(self, writer, indent="", addindent="", newl=""):
        """
        Write the continuous  dataset using sonic visualiser xml conventions
        """
        # dataset = self.data.appendChild(self.doc.createElement('dataset'))
        # dataset.setAttribute('id', str(imodel))
        # dataset.setAttribute('dimensions', '2')
        writer.write('%s<dataset id="%s" dimensions="%s">%s' % (indent, self.datasetid, self.dimensions, newl))
        indent2 = indent + addindent
        if self.values is not None:
            for l, x, y in zip(self.labels, self.frames, self.values):
                writer.write('%s<point label="%s" frame="%d" value="%f"/>%s' % (indent2, self.int2label[l], x, y, newl))
        else:
            for x, l in zip(self.frames, self.labels):
                writer.write('%s<point frame="%d" label="%s"/>%s' % (indent2, x, self.int2label[l], newl))
        writer.write('%s</dataset>%s' % (indent, newl))



class SVDataset1D(SVDataset):
    """
    This class is aimed at storing large datasets in minidom documents
    datasets are stored as iterable structure (lists, numpy arrays, ...)
    This data is converted to sonic visualiser point nodes at writing time
    This allows to avoid the storage of very large xml trees in RAM,
    and avoid swap
    """

    def __init__(self, domdoc, datasetid, samplerate):
        SVDataset.__init__(self, domdoc, datasetid, samplerate)
        self.dimensions = 1
        self.values = None

    def set_data_from_iterable(self, frames, labels=None):
        SVDataset.set_data_from_iterable(self, frames, None, labels)


class SVDataset2D(SVDataset):
    """
    This class is aimed at storing large datasets in minidom documents
    datasets are stored as iterable structure (lists, numpy arrays, ...)
    This data is converted to sonic visualiser point nodes at writing time
    This allows to avoid the storage of very large xml trees in RAM,
    and avoid swap 
    """
    def __init__(self, domdoc, datasetid, samplerate):
        SVDataset.__init__(self, domdoc, datasetid, samplerate)
        self.dimensions = 2


class SVDataset3D(SVDataset2D):

    def __init__(self, domdoc, datasetid, samplerate):
        SVDataset2D.__init__(self, domdoc, datasetid, samplerate)
        self.durations = []
        self.dimensions = 3

    def set_data_from_iterable(self, frames, values, durations, labels=None):
        SVDataset2D.set_data_from_iterable(self, frames, values, labels)
        if not isinstance(durations, collections.Iterable):
            raise TypeError("durations must be an iterable")
        assert(len(self.frames) == len(durations))
        self.durations = durations

    def append_xml_point(self, attrs):
        SVDataset2D.append_xml_point(self, attrs)
        self.durations.append(float(attrs.getValue('duration')))

    def writexml(self, writer, indent="", addindent="", newl=""):
        """
        Write the continuous  dataset using sonic visualiser xml conventions
        """
        writer.write('%s<dataset id="%s" dimensions="%s">%s' % (indent, self.datasetid, self.dimensions, newl))
        indent2 = addindent + indent
        for l, x, y, d in zip(self.labels, self.frames, self.values, self.durations):
            writer.write('%s<point label="%s" frame="%d" value="%f" duration="%d"/>%s' % (indent2, self.int2label[l], x, y, d, newl))
        writer.write('%s</dataset>%s' % (indent, newl))
