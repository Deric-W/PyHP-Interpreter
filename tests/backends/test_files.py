#!/usr/bin/python3

"""Tests for pyhp.backends.files"""

import unittest
import sys
import re
import io
import os
import os.path
import inspect
import importlib.util
import importlib.machinery
from pyhp.backends import SourceInfo
from pyhp.backends.files import (
    FileSource,
    Directory,
    SourceFileLoader,
    LeavesDirectoryError,
    StrictDirectory
)
from pyhp.compiler.parsers import RegexParser
from pyhp.compiler.generic import GenericCodeBuilder
from pyhp.compiler.util import Compiler, Dedenter


compiler = Compiler(
    RegexParser(
        re.compile(r"<\?pyhp\s"),
        re.compile(r"\s\?>")
    ),
    Dedenter(
        GenericCodeBuilder(-1)
    )
)

compiler2 = Compiler(
    RegexParser(
        re.compile(r"<\?pyhp\s"),
        re.compile(r"\s\?>")
    ),
    GenericCodeBuilder(0)   # different than compiler!
)


class TestFileSource(unittest.TestCase):
    """test FileSource"""
    def test_eq(self) -> None:
        """test FileSource.__eq__"""
        sources = [
            FileSource(
                io.FileIO(sys.stdin.fileno(), "r", closefd=False),
                compiler
            ),
            FileSource(
                io.FileIO("tests/embedding/syntax.pyhp", "r"),
                compiler
            ),
            FileSource(
                io.FileIO("tests/embedding/syntax.pyhp", "r"),
                compiler2
            )
        ]
        try:
            for source in sources:
                self.assertEqual(
                    [source],
                    [s for s in sources if s == source]
                )
        finally:
            for source in sources:
                source.close()

    def test_code(self) -> None:
        """test FileSource.code"""
        with open("tests/embedding/syntax.pyhp", "r", newline="") as fd, \
                FileSource(io.FileIO("tests/embedding/syntax.pyhp", "r"), compiler) as source:
            loader = SourceFileLoader("__main__", "tests/embedding/syntax.pyhp")
            code = compiler.compile_file(fd, loader)
            code2 = source.code()
            code3 = source.code()   # check if source can be read multiple times
            self.assertEqual(code, code2)
            self.assertEqual(code2, code3)

    def test_spec(self) -> None:
        """test code spec"""
        with FileSource(io.FileIO("tests/embedding/syntax.pyhp", "r"), compiler) as source:
            spec1 = source.code().spec  # type: ignore
            spec2 = FileSource(         # type: ignore
                io.FileIO(source.fd.fileno(), "r", closefd=False),
                compiler
            ).code().spec
        self.assertEqual(spec1.name, "__main__")
        self.assertEqual(spec1.origin, "tests/embedding/syntax.pyhp")
        self.assertTrue(spec1.has_location)
        self.assertEqual(spec2.name, "__main__")
        self.assertFalse(spec2.has_location)

    def test_source(self) -> None:
        """test FileSource.source"""
        with open("tests/embedding/syntax.pyhp", "r") as fd, \
                FileSource(io.FileIO("tests/embedding/syntax.pyhp", "r"), compiler) as source:
            # workaround git automatic newlines
            self.assertEqual(fd.read(), source.source().replace(os.linesep, "\n"))

    def test_size(self) -> None:
        """test FileSource.size"""
        with FileSource(io.FileIO("tests/embedding/syntax.pyhp", "r"), compiler) as source:
            self.assertEqual(source.size(), len(source.source()))

    def test_introspection(self) -> None:
        """test code introspection"""
        with FileSource(io.FileIO("tests/embedding/syntax.pyhp", "r"), compiler) as source:
            loader = SourceFileLoader("__main__", "tests/embedding/syntax.pyhp")
            spec = importlib.machinery.ModuleSpec(
                "__main__",
                loader,
                origin="tests/embedding/syntax.pyhp",
                is_package=False
            )
            spec.has_location = True
            self.assertEqual(
                source.source().replace(os.linesep, "\n"),  # workaround git automatic newlines
                inspect.getsource(importlib.util.module_from_spec(spec))
            )
        with self.assertRaises(ImportError):
            loader.get_code("test")
        with self.assertRaises(ImportError):
            loader.get_source("test")

    def test_timestamps(self) -> None:
        """test FileSource timestamps"""
        # allow parallel execution of file reading tests
        with FileSource(io.FileIO("tests/__init__.py", "r"), compiler) as source:
            info = source.info()
            self.assertEqual(
                info,
                (
                    source.mtime(),
                    source.ctime(),
                    source.atime()
                )
            )
            stat = os.stat("tests/__init__.py")
            self.assertEqual(   # might fail if atime gets recorded for __init__.py
                info,
                (
                    stat.st_mtime_ns,
                    stat.st_ctime_ns,
                    stat.st_atime_ns
                )
            )


class TestDirectory(unittest.TestCase):
    """test Directory"""

    container = Directory(
        "tests/embedding",
        compiler
    )

    abs_container = Directory(
        os.path.abspath("tests/embedding"),
        compiler
    )

    def test_config(self) -> None:
        """test Directory.from_config"""
        self.assertEqual(
            self.container,
            Directory.from_config(
                {
                    "path": "tests/embedding"
                },
                compiler
            )
        )
        self.assertEqual(
            Directory.from_config(
                {
                    "path": "~/test"
                },
                compiler
            ).directory_path,
            os.path.expanduser("~/test")
        )
        with self.assertRaises(ValueError):
            Directory.from_config(
                {
                    "path": 9
                },
                compiler
            )
        with self.assertRaises(ValueError):
            Directory.from_config(
                {
                    "path": "tests/embedding"
                },
                self.container
            )

    def test_access(self) -> None:
        """test Directory code retrieval"""
        for name, source in self.container.items():
            with source:
                path = os.path.join("tests/embedding", name)
                with open(path, "r", newline="") as fd:
                    self.assertEqual(
                        source.code(),
                        compiler.compile_file(fd, SourceFileLoader("__main__", path))
                    )

    def test_iter(self) -> None:
        """test iter(Directory)"""
        files = {   # set -> no order
            "syntax.pyhp",
            "syntax.output",
            "indentation.pyhp",
            "indentation.output",
            "shebang.pyhp",
            "shebang.output"
        }
        self.assertEqual(
            files,
            self.container.keys()
        )
        self.assertEqual(
            files,
            self.abs_container.keys()
        )

    def test_eq(self) -> None:
        """test Directory.__eq__"""
        directories = [
            self.container,
            Directory(
                "null",
                compiler
            ),
            Directory(
                self.container.directory_path,
                compiler2
            ),
            self.abs_container
        ]
        self.assertEqual(
            [self.container],
            [directory for directory in directories if directory == self.container]
        )

    def test_contains(self) -> None:
        """test Directory.__contains__"""
        for name in self.container.keys():
            self.assertIn(name, self.container)
        self.assertNotIn("abc", self.container)
        self.assertNotIn(1, self.container)

    def test_mtime(self) -> None:
        """test Directory.mtime"""
        self.assertEqual(
            self.container.mtime("syntax.pyhp"),
            os.stat("tests/embedding/syntax.pyhp").st_mtime_ns
        )

    def test_ctime(self) -> None:
        """test Directory.ctime"""
        self.assertEqual(
            self.container.ctime("syntax.pyhp"),
            os.stat("tests/embedding/syntax.pyhp").st_ctime_ns
        )

    def test_atime(self) -> None:
        """test Directory.atime"""
        self.assertEqual(
            self.container.atime("syntax.pyhp"),
            os.stat("tests/embedding/syntax.pyhp").st_atime_ns
        )

    def test_info(self) -> None:
        """test Directory.info"""
        stat = os.stat("tests/embedding/syntax.pyhp")
        self.assertEqual(
            self.container.info("syntax.pyhp"),
            SourceInfo(
                stat.st_mtime_ns,
                stat.st_ctime_ns,
                stat.st_atime_ns
            )
        )


class TestStrictDirectory(unittest.TestCase):
    """test StrictDirectory"""

    container = StrictDirectory(
        "tests/embedding",
        compiler
    )

    abs_container = StrictDirectory(
        os.path.abspath("tests/embedding"),
        compiler
    )

    def test_traversal(self) -> None:
        """test resistance against path traversal"""
        for name in ("../test1", "a/../../test3", "../testsX"):  # would leave the directory
            with self.assertRaises(LeavesDirectoryError):
                self.container[name].close()
            with self.assertRaises(LeavesDirectoryError):
                self.abs_container[name].close()
        with self.assertRaises(ValueError):     # would leave directory on cwd change
            self.container[os.path.abspath("test/embedding/syntax.pyhp")].close()
        # would not leave directory on cwd change
        self.abs_container[os.path.abspath("tests/embedding/syntax.pyhp")].close()
        for name in ("syntax.pyhp", "../embedding/syntax.pyhp", "./syntax.pyhp"):   # inside path
            self.container[name].close()
            self.abs_container[name].close()

    def test_contains(self) -> None:
        """test Directory.__contains__"""
        for name in self.container.keys():
            self.assertIn(name, self.container)
        self.assertNotIn("abc", self.container)
        self.assertNotIn("../../../../abc", self.container)
        self.assertNotIn(1, self.container)
