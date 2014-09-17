# -*- coding: utf-8 -*-
"""
docstring goes here.

:copyright: Copyright 2014 by the Elephant team, see AUTHORS.txt.
:license: Modified BSD, see LICENSE.txt for details.
"""

import os
import tempfile
import unittest

import elephant.file_tools as ft


class FilterByExtensionsTestCase(unittest.TestCase):
    def setUp(self):
        self.fnames = ['test0.h5',
                       'test1h5',
                       'test2.h5.jpg',
                       'test3.jpg',
                       'test4.raw',
                       'test5.txt',
                       'test6.ptxt',
                       'test7.dat']

    def test__filter_by_extensions__single(self):
        ext = 'raw'
        ft.filter_by_extensions(self.fnames, ext)
        targ = ['test4.raw']
        self.assertEqual(targ, self.fnames)

    def test__filter_by_extensions__multi(self):
        ext = ['h5', '.txt', 'dat']
        ft.filter_by_extensions(self.fnames, ext)
        targ = ['test0.h5',
                'test5.txt',
                'test7.dat']
        self.assertEqual(targ, self.fnames)


class YieldFilesPathsTestCase(unittest.TestCase):
    def full_file_list(self, filelist):
        return [os.path.join(self.targdir, *ifile) for ifile in filelist]

    def full_dir_list(self, filelist):
        newfilelist = (ifile[:-1] for ifile in filelist)
        return self.full_file_list(newfilelist)

    def setUp(self):
        self.maxDiff = None

        self.targdir = os.path.join(tempfile.gettempdir(),
                                    'elephant', 'file_tools')

        filelist = [('test0', 'test00', 'test000', 'test0000.h5'),
                    ('test0', 'test00', 'test000', 'test0001.txt'),
                    ('test0', 'test00', 'test000', 'test0002.dat'),
                    ('test0', 'test01', 'test010.dat'),
                    ('test0', 'test02', 'test020.txt'),
                    ('test0', 'test03', 'test030.h5'),
                    ('test1', 'test10', 'test100', 'test1000.h5'),
                    ('test1', 'test10', 'test101', 'test1010.txt'),
                    ('test1', 'test10', 'test102', 'test1020.dat'),
                    ('test2', 'test20.h5'),
                    ('test2', 'test21.h5'),
                    ('test2', 'test22.h5'),
                    ('test0a.h5',),
                    ('test1a.txt',),
                    ('test2a.dat',),
                    ('test0b.h5',),
                    ('test1b.dat',),
                    ('test2b.txt',),
                    ('test0c.dat',),
                    ('test1c.txt',),
                    ('test2c.h5',)]
        linklist = [('link0', 'test00', 'test000', 'test0000.h5'),
                    ('link0', 'test00', 'test000', 'test0001.txt'),
                    ('link0', 'test00', 'test000', 'test0002.dat'),
                    ('link0', 'test01', 'test010.dat'),
                    ('link0', 'test02', 'test020.txt'),
                    ('link0', 'test03', 'test030.h5')]

        linktargdir = os.path.join(self.targdir, 'test0')
        linkdir = os.path.join(self.targdir, 'link0')

        dirlist =sorted(self.full_dir_list(filelist))
        self.pathlist = sorted(self.full_file_list(filelist))
        self.linkpathlist = sorted(self.full_file_list(linklist) +
                                   self.pathlist)

        for idir in dirlist:
            if not os.path.exists(idir):
                os.makedirs(idir)

        for ifile in self.pathlist:
            if not os.path.exists(ifile):
                with open(ifile, 'w') as fobj:
                    fobj.write('\n\n')

        if not os.path.exists(linkdir):
            os.symlink(linktargdir, linkdir)

    def test__yield_files_paths__default(self):
        res0 = ft.yield_files_paths(targdir=self.targdir)
        res1 = ft.yield_files_paths(targdir=self.targdir, rescursive=False)
        res2 = ft.yield_files_paths(targdir=self.targdir, extensions=None)
        res3 = ft.yield_files_paths(targdir=self.targdir, extensions=[])
        res4 = ft.yield_files_paths(targdir=self.targdir, filefilters=None)
        res5 = ft.yield_files_paths(targdir=self.targdir, filefilters=[])
        res6 = ft.yield_files_paths(targdir=self.targdir, dirfilters=None)
        res7 = ft.yield_files_paths(targdir=self.targdir, dirfilters=[])
        res8 = ft.yield_files_paths(targdir=self.targdir, followlinks=False)
        res9 = ft.yield_files_paths(targdir=self.targdir, followlinks=True)

        res0 = sorted(list(res0))
        res1 = sorted(list(res1))
        res2 = sorted(list(res2))
        res3 = sorted(list(res3))
        res4 = sorted(list(res4))
        res5 = sorted(list(res5))
        res6 = sorted(list(res6))
        res7 = sorted(list(res7))
        res8 = sorted(list(res8))
        res9 = sorted(list(res9))

        targ = [('test0a.h5',),
                ('test1a.txt',),
                ('test2a.dat',),
                ('test0b.h5',),
                ('test1b.dat',),
                ('test2b.txt',),
                ('test0c.dat',),
                ('test1c.txt',),
                ('test2c.h5',)]
        targ = sorted(self.full_file_list(targ))

        self.assertEqual(targ, res0)
        self.assertEqual(targ, res1)
        self.assertEqual(targ, res2)
        self.assertEqual(targ, res3)
        self.assertEqual(targ, res4)
        self.assertEqual(targ, res5)
        self.assertEqual(targ, res6)
        self.assertEqual(targ, res7)
        self.assertEqual(targ, res8)
        self.assertEqual(targ, res9)

    def test__yield_files_paths__recursive(self):
        res0 = ft.yield_files_paths(targdir=self.targdir, rescursive=True)
        res1 = ft.yield_files_paths(targdir=self.targdir, rescursive=True,
                                    extensions=None)
        res2 = ft.yield_files_paths(targdir=self.targdir, rescursive=True,
                                    extensions=[])
        res3 = ft.yield_files_paths(targdir=self.targdir, rescursive=True,
                                    filefilters=None)
        res4 = ft.yield_files_paths(targdir=self.targdir, rescursive=True,
                                    filefilters=[])
        res5 = ft.yield_files_paths(targdir=self.targdir, rescursive=True,
                                    dirfilters=None)
        res6 = ft.yield_files_paths(targdir=self.targdir, rescursive=True,
                                    dirfilters=[])
        res7 = ft.yield_files_paths(targdir=self.targdir, rescursive=True,
                                    followlinks=False)

        res0 = sorted(list(res0))
        res1 = sorted(list(res1))
        res2 = sorted(list(res2))
        res3 = sorted(list(res3))
        res4 = sorted(list(res4))
        res5 = sorted(list(res5))
        res6 = sorted(list(res6))
        res7 = sorted(list(res7))

        targ = self.pathlist

        self.assertEqual(targ, res0)
        self.assertEqual(targ, res1)
        self.assertEqual(targ, res2)
        self.assertEqual(targ, res3)
        self.assertEqual(targ, res4)
        self.assertEqual(targ, res5)
        self.assertEqual(targ, res6)
        self.assertEqual(targ, res7)

    def test__yield_files_paths__recursive_followlinks(self):
        res0 = ft.yield_files_paths(targdir=self.targdir,
                                    rescursive=True, followlinks=True)
        res1 = ft.yield_files_paths(targdir=self.targdir,
                                    rescursive=True, followlinks=True,
                                    extensions=None)
        res2 = ft.yield_files_paths(targdir=self.targdir,
                                    rescursive=True, followlinks=True,
                                    extensions=[])
        res3 = ft.yield_files_paths(targdir=self.targdir,
                                    rescursive=True, followlinks=True,
                                    filefilters=None)
        res4 = ft.yield_files_paths(targdir=self.targdir,
                                    rescursive=True, followlinks=True,
                                    filefilters=[])
        res5 = ft.yield_files_paths(targdir=self.targdir,
                                    rescursive=True, followlinks=True,
                                    dirfilters=None)
        res6 = ft.yield_files_paths(targdir=self.targdir,
                                    rescursive=True, followlinks=True,
                                    dirfilters=[])

        res0 = sorted(list(res0))
        res1 = sorted(list(res1))
        res2 = sorted(list(res2))
        res3 = sorted(list(res3))
        res4 = sorted(list(res4))
        res5 = sorted(list(res5))
        res6 = sorted(list(res6))

        targ = self.linkpathlist

        self.assertEqual(targ, res0)
        self.assertEqual(targ, res1)
        self.assertEqual(targ, res2)
        self.assertEqual(targ, res3)
        self.assertEqual(targ, res4)
        self.assertEqual(targ, res5)
        self.assertEqual(targ, res6)


if __name__ == '__main__':
    unittest.main()
