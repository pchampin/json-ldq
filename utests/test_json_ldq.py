from __future__ import unicode_literals

from json import load
from os.path import dirname, join
from sys import path
from unittest import TestCase

from nose.tools import assert_equal, assert_items_equal
from rdflib import Graph, BNode as B, Literal as L, URIRef as U, Variable as V
from rdflib.compare import isomorphic


path.append(join(dirname(dirname(__file__)), "lib"))

from json_ldq import apply, quote_variables


def test_quote_variables():
    for obj, expected in [
        # simple cases ('*2' means that obj == expected)
        ("foo",) *2,
        (42,) *2,
        (True,) *2,
        ({"a": "foo", "b": 42, "c": True},) *2,
        (["foo", 42, True, {}],) *2,
        # @var replacement
        ({"@var": "?x"}, {"@id": "x-json-ldq-var://?x"}),
        ([42, {"@var": "?x"}], [42, {"@id": "x-json-ldq-var://?x"}]),
        ({"a": [42, {"@var": "?x"}]}, {"a": [42, {"@id": "x-json-ldq-var://?x"}]}),
        # @var replacement in dicts (@id is a special case)
        ({"a": {"@var": "?x"}}, {"a": {"@id": "x-json-ldq-var://?x"}}),
        ({"@id": {"@var": "?x"}}, {"@id": "x-json-ldq-var://?x"}),
        # pathological case (@id looks like variable)
        ({"@id": "?x", "a": "foo"},) *2,
    ]:
        got = quote_variables(obj)
        yield assert_equal, got, expected

EXAMPLES = join(dirname(dirname(__file__)), "examples")

class TestQueries(TestCase):
    def setUp(self):
        self.g = Graph()
        #with open(join(EXAMPLES, "data.ttl")) as data_file:
        #    self.g.load(data_file, format="turtle")
        self.g.load(join(EXAMPLES, "data.ttl"), format="turtle")

    def tearDown(self):
        pass

    def test_query1(self):
        with open(join(EXAMPLES, "query1.json")) as query_file:
            q = load(query_file)
        results = apply(q, self.g)
        assert_items_equal(results.bindings, [
            {
                #V("p"): U("http://example.org/bob"),
                V("n"): L("Bob"),
            },
            {
                #V("p"): B("charlie"),
                V("n"): L("Charlie"),
            },
            {
                #V("p"): U("http://example.org/dan"),
                V("n"): L("Dan"),
            },
        ])

    def test_query2(self):
        with open(join(EXAMPLES, "query2.json")) as query_file:
            q = load(query_file)
        result = apply(q, self.g)
        expected = Graph()
        expected.load(join(EXAMPLES, "query2.result.ttl"), format="turtle")
        assert isomorphic(result.graph, expected), result.graph.serialize(format="turtle")
