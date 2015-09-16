"""
JSON-LDQ: A JSON-based query language for Linked Data
"""
__version__ = "0.1"

import logging

from pyld import jsonld

LOG = logging.getLogger(__name__)

def apply(query, graph):

    select = query.get('@select')
    if select is not None:
        assert "@construct" not in query
        if type(select) is list:
            select = " ".join(select)
        sparql = "SELECT {}\n".format(select)
    else:
        construct = query['@construct']
        sparql = "CONSTRUCT {}".format(_build_clause(query, '@construct'))

    sparql = "{}WHERE {}".format(sparql, _build_clause(query, '@where'))

    orderby = query.get('@orderby')
    if orderby:
        if type(orderby) is list:
            orderby = " ".join(orderby)
        sparql = "{}ORDER BY {}\n".format(orderby)
    limit = query.get('@limit')
    if limit is not None:
        sparql = "{}LIMIT {}\n".format(limit)
    offset = query.get('@offset')
    if offset is not None:
        sparql = "{}OFFSET {}\n".format(offset)



    LOG.debug("SPARQL: %s", sparql)
    return graph.query(sparql)



def _build_clause(query, clause_key):
    prepared_clause = quote_variables(query[clause_key])
    global_context = query.get('@context')
    if global_context:
        prepared_clause['@context'] = _context_concat(global_context,
                                                      prepared_clause.get('@context'))
    LOG.debug("Prepared clause (%s): %s", clause_key, prepared_clause)

    sparql = "{\n"
    normalized = jsonld.normalize(prepared_clause)
    for graphid, triples in normalized.items():
        if graphid != '@default':
            if graphid.startswith(VAR_PREFIX):
                graphid = graphid[len(VAR_PREFIX):]
            else:
                graphid = "<{}>".format(graphid)
            sparql = '{}  GRAPH {} {{\n'.format(sparql, graphid)
        for triple in triples:
            sparql = '{}    '.format(sparql)
            for key in ('subject', 'predicate', 'object'):
                node = triple[key]
                ntype = node['type']
                value = node['value']
                if ntype == 'IRI':
                    if value.startswith(VAR_PREFIX):
                        value = value[len(VAR_PREFIX):]
                    else:
                        value = "<{}>".format(value)
                elif ntype == 'blank node':
                    pass #value has alreadt the correct form
                else:
                    assert ntype == 'literal', ntype
                    if 'datatype' in node:
                        value = "{}^^<{}>".format(dumps(value), node['datatype'])
                    else:
                        value = "{}@{}".format(dumps(value), node['language'])
                sparql = '{}{} '.format(sparql, value)
            sparql = '{}.\n'.format(sparql)
        if graphid != '@default':
            sparql = '{}  }}\n'.format(sparql)
    sparql = "{}}}\n".format(sparql)
    return sparql


def quote_variables(obj, key=None):
    if type(obj) is dict:
        varname = obj.get('@var')
        if varname is not None:
            if len(obj) > 1:
                raise JsonLDQError("must not mix @var with other attributes")
            if type(varname) is not unicode:
                raise JsonLDQError(
                    "@val must be a string (got {})".format(type(val)))
            quoted_var = "{}{}".format(VAR_PREFIX, obj['@var'])
            if key == '@id':
                return quoted_var
            else:
                return {"@id": quoted_var}
        else:
            return { key:quote_variables(val, key) for key,val in obj.items() }
    elif type(obj) is list:
        return [ quote_variables(elt) for elt in obj ]
    else:
        return obj

def _context_concat(ctx1, ctx2):
    if ctx2 is None:
        return ctx1
    if type(ctx1) != list:
        ctx1 = [ctx1]
    if type(ctx2) != list:
        ctx2 = [ctx2]
    return ctx1 + ctx2



class JsonLDQError(Exception):
    pass

VAR_PREFIX = "x-json-ldq-var://"