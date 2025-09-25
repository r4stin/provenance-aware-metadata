from pyshacl import validate
from rdflib import Graph

g = Graph().parse("metadata/record.jsonld", format="json-ld")
sh = Graph().parse("metadata/shacl.ttl", format="turtle")

conforms, results_graph, results_text = validate(
    data_graph=g, shacl_graph=sh, inference='rdfs', abort_on_first=False
)
print("Conforms:", conforms)
print(results_text)
