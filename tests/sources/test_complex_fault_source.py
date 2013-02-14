#!/usr/bin/env/python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# LICENSE
#
# Copyright (c) 2010-2013, GEM Foundation, G. Weatherill, M. Pagani,
# D. Monelli.
#
# The Hazard Modeller's Toolkit is free software: you can redistribute
# it and/or modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>
#
# DISCLAIMER
# 
# The software Hazard Modeller's Toolkit (hmtk) provided herein
# is released as a prototype implementation on behalf of
# scientists and engineers working within the GEM Foundation (Global
# Earthquake Model).
#
# It is distributed for the purpose of open collaboration and in the
# hope that it will be useful to the scientific, engineering, disaster
# risk and software design communities.
#
# The software is NOT distributed as part of GEM's OpenQuake suite
# (http://www.globalquakemodel.org/openquake) and must be considered as a
# separate entity. The software provided herein is designed and implemented
# by scientific staff. It is not developed to the design standards, nor
# subject to same level of critical review by professional software
# developers, as GEM's OpenQuake software suite.
#
# Feedback and contribution to the software is welcome, and can be
# directed to the hazard scientific staff of the GEM Model Facility
# (hazard@globalquakemodel.org).
#
# The Hazard Modeller's Toolkit (hmtk) is therefore distributed WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# The GEM Foundation, and the authors of the software, assume no
# liability for use of the software.

# -*- coding: utf-8 -*-

'''
Tests the construction and methods within the :class: 
hmtk.sources.complex_fault_source.mtkComplexFaultSource
'''

import unittest
import warnings
import numpy as np
from nhlib.geo import point, line
from nhlib.geo.surface.complex_fault import ComplexFaultSurface
from hmtk.sources.complex_fault_source import mtkComplexFaultSource
from hmtk.seismicity.catalogue import Catalogue
from hmtk.seismicity.selector import CatalogueSelector

SOURCE_ATTRIBUTES = ['typology', 'mfd', 'name', 'geometry', 'rake', 
                     'mag_scale_rel', 'upper_depth', 'catalogue', 
                     'rupt_aspect_ratio', 'lower_depth', 'id', 'trt']
                     
class TestComplexFaultSource(unittest.TestCase):
    '''
    Test module for the hmtk.sources.complex_fault_source.mtkComplexFaultSource
    class
    '''
    def setUp(self):
        warnings.simplefilter("ignore")
        self.catalogue = Catalogue()
        self.fault_source = None
        self.trace_line = [line.Line([point.Point(1.0, 0.0, 1.0),
                                     point.Point(0.0, 1.0, 0.9)])]
        self.trace_line.append(line.Line([point.Point(1.2, 0.0, 40.),
                                          point.Point(1.0, 1.0, 45.),
                                          point.Point(0.0, 1.3, 42.)]))
        self.trace_array = [np.array([[1.0, 0.0, 1.0], [0.0, 1.0, 0.9]])]
        self.trace_array.append(np.array([[1.2, 0.0, 40.],
                                          [1.0, 1.0, 45.],
                                          [0.0, 1.3, 42.]]))

        
    def test_simple_fault_instantiation(self):
        '''
        Tests the core instantiation of the module
        '''
        # Simple instantiation - minimual data
        self.fault_source = mtkComplexFaultSource('101', 'A complex fault')
        self.assertEqual(self.fault_source.id, '101')
        self.assertEqual(self.fault_source.name, 'A complex fault')
        self.assertEqual(self.fault_source.typology, 'ComplexFault')
        self.assertListEqual(self.fault_source.__dict__.keys(),
                             SOURCE_ATTRIBUTES)

    def test_get_minmax_edges(self):
        '''
        Tests the private method to extract the minimum and maximum depth
        from a set of edges
        '''
        self.fault_source = mtkComplexFaultSource('101', 'A complex fault')
        # Test case simple edge
        self.fault_source._get_minmax_edges(self.trace_line[0])
        self.assertAlmostEqual(self.fault_source.upper_depth, 0.9)
        self.assertAlmostEqual(self.fault_source.lower_depth, 1.0)
        self.fault_source._get_minmax_edges(self.trace_line[1])
        self.assertAlmostEqual(self.fault_source.upper_depth, 0.9)
        self.assertAlmostEqual(self.fault_source.lower_depth, 45.0)
        
        # Check the same behaviour when input as array
        self.fault_source = mtkComplexFaultSource('101', 'A complex fault')
        # Test case simple edge
        self.fault_source._get_minmax_edges(self.trace_array[0])
        self.assertAlmostEqual(self.fault_source.upper_depth, 0.9)
        self.assertAlmostEqual(self.fault_source.lower_depth, 1.0)
        self.fault_source._get_minmax_edges(self.trace_array[1])
        self.assertAlmostEqual(self.fault_source.upper_depth, 0.9)
        self.assertAlmostEqual(self.fault_source.lower_depth, 45.0)

    def test_create_complex_geometry(self):
        '''
        Tests the complex geometry creation
        '''
        self.fault_source = mtkComplexFaultSource('101', 'A complex fault')
        # Test case when input as list of nhlib.geo.line.Line
        self.fault_source.create_geometry(self.trace_line, mesh_spacing = 2.0)
        self.assertIsInstance(self.fault_source.geometry, ComplexFaultSurface)
        # Use the dip as a simple indicator of geometrical success!
        self.assertAlmostEqual(self.fault_source.dip, 40.5398531, 2)

        # Create a second instance 
        fault2 = mtkComplexFaultSource('101', 'A complex fault')
        fault2.create_geometry(self.trace_array, mesh_spacing = 2.0)
        self.assertIsInstance(fault2.geometry, ComplexFaultSurface)
        # Compare it to the first
        self.assertAlmostEqual(self.fault_source.dip, fault2.dip)

        # If less than two edges are input ensure error is raised
        bad_traces = [line.Line([point.Point(1.0, 0.0, 3.0),
                                 point.Point(1.0, 0.0, 3.0)])]
        
        self.fault_source = mtkComplexFaultSource('101', 'A complex fault')
        with self.assertRaises(ValueError) as ver:
            self.fault_source.create_geometry(bad_traces)
        self.assertEqual(ver.exception.message, 'Complex fault geometry '
                                                'incorrectly defined')

        # If an edge is not defined from either a nhlib.geo.line.Line instance
        # or numpy.ndarray then ensure error is raised
        
        bad_traces = [line.Line([point.Point(1.0, 0.0, 3.0),
                                 point.Point(1.0, 0.0, 3.0)])]
        bad_traces.append('a bad input')

        self.fault_source = mtkComplexFaultSource('101', 'A complex fault')
        with self.assertRaises(ValueError) as ver:
            self.fault_source.create_geometry(bad_traces)
        self.assertEqual(ver.exception.message, 'Unrecognised or unsupported '
                                                'geometry definition')

    def test_select_within_distance(self):
        '''
        Tests the selection of earthquakes within distance of fault
        '''
        # Create fault
        self.fault_source = mtkComplexFaultSource('101', 'A complex fault')
        # Test case when input as list of nhlib.geo.line.Line
        self.fault_source.create_geometry(self.trace_line, mesh_spacing = 2.0)
        self.assertIsInstance(self.fault_source.geometry, ComplexFaultSurface)

        # Create simple catalogue
        self.catalogue.data['longitude'] = np.arange(0., 4.1, 0.1)
        self.catalogue.data['latitude'] = np.arange(0., 4.1, 0.1)
        self.catalogue.data['depth'] = np.ones(41, dtype=float)
        self.catalogue.data['eventID'] = np.arange(0, 41, 1)
        selector0 = CatalogueSelector(self.catalogue)

        # Test when considering Joyner-Boore distance
        self.fault_source.select_catalogue(selector0, 50.)
        np.testing.assert_array_equal(
            self.fault_source.catalogue.data['eventID'],
            np.arange(2, 14, 1))

        # Test when considering rupture distance
        self.fault_source.select_catalogue(selector0, 
                                                           50.,
                                                           'rupture')
        np.testing.assert_array_equal(
            self.fault_source.catalogue.data['eventID'],
            np.arange(2, 12, 1))

        # The usual test to ensure error is raised when no events in catalogue
        self.catalogue = Catalogue()
        selector0 = CatalogueSelector(self.catalogue)
        with self.assertRaises(ValueError) as ver:
            self.fault_source.select_catalogue(selector0, 40.0)
        self.assertEqual(ver.exception.message, 
                         'No events found in catalogue!')
                         
    def tearDown(self):
        warnings.resetwarnings()