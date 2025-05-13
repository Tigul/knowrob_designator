import uuid

class DesignatorParser:
    def __init__(self):
        self.triples = []

    # Mockup for the parse method
    def parse(self, designator):
        """
        Parse a designator dictionary into RDF-style triples.

        Args:
            designator (dict): JSON-like nested structure

        Returns:
            list of (subject, predicate, object) triples
        """
        triples = [
            ("a", "rdf:type", "Transporting"),
            ("a", "hasChild", "b"),
            ("b", "rdf:type", "anAction"),
            ("b", "objectActedOn", "c"),
            ("c", "rdf:type", "anObject"),
            ("c", "name", "Milk"),
            ("b", "target", "d"),
            ("d", "rdf:type", "theLocation"),
            ("d", "goal", "e"),
            ("e", "rdf:type", "theObject"),
            ("e", "name", "Table1")
        ]
        return triples

    def parse(self, designator_json, root=None):
        """
        Iteratively convert a nested designator JSON into RDF-style triples.

        :param designator_json: dict (parsed JSON structure)
        :param root: optional root URI
        :return: list of (subject, predicate, object) triples
        """
        self.triples.clear()
        root_id = root or self._new_designator_id()

        # Stack of (current_subject, current_object)
        stack = [(root_id, designator_json)]

        while stack:
            subject, current = stack.pop()

            if not isinstance(current, dict):
                continue

            for key, value in current.items():
                predicate = self._predicate(key)

                if isinstance(value, dict):
                    sub_id = self._new_designator_id()
                    self.triples.append((subject, predicate, sub_id))
                    stack.append((sub_id, value))

                elif isinstance(value, list):
                    for v in value:
                        if isinstance(v, dict):
                            sub_id = self._new_designator_id()
                            self.triples.append((subject, predicate, sub_id))
                            stack.append((sub_id, v))
                        else:
                            self.triples.append((subject, predicate, self._literal(v)))

                else:
                    self.triples.append((subject, predicate, self._literal(value)))

        return self.triples

    def _new_designator_id(self):
        return f"desig:{uuid.uuid4()}"

    def _predicate(self, key):
        return f"knowrob:{key}"

    def _literal(self, value):
        if isinstance(value, str):
            return f"\"{value}\""
        return str(value)
