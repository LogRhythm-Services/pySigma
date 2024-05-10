import re
from sigma.backends.base import BaseBackend
from sigma.parser.condition import NodeSubexpression, ConditionAND, ConditionOR, ConditionNOT, ConditionNULLValue, ConditionFieldEqualsValueExpression
from sigma.parser.modifiers.type import SigmaRegularExpressionModifier

class LogRhythmBackend(BaseBackend):
    """Converts Sigma rule into Lucene query string for LogRhythm. Only searches, no aggregations."""
    identifier = "logrhythm"
    active = True

    reEscape = re.compile(r"([+\=!(){}\[\]^\"~:/]|(?<!\\)\\(?![*?\\])|\\u|&&|\|\|)")
    andToken = " AND "
    orToken = " OR "
    notToken = "NOT "
    subExpression = "(%s)"
    listExpression = "(%s)"
    listSeparator = " OR "
    valueExpression = "%s"
    typedValueExpression = {
        SigmaRegularExpressionModifier: "/%s/"
    }
    nullExpression = "NOT _exists_:%s"
    notNullExpression = "_exists_:%s"
    mapExpression = "%s:%s"
    mapListsSpecialHandling = False
    wildcard_use_keyword = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize any LogRhythm-specific configurations

    def generateQuery(self, parsed):
        # Start building the query from the parsed Sigma rule
        query = ""
        if parsed.conditions:
            query = self.parse_condition(parsed.parsedSearch)
        return query

    def parse_condition(self, condition):
        if isinstance(condition, NodeSubexpression):
            # Handle subexpressions, potentially recursive
            return self.subExpression % self.parse_condition(condition.item)
        elif isinstance(condition, ConditionAND):
            return self.andToken.join(self.parse_condition(c) for c in condition)
        elif isinstance(condition, ConditionOR):
            return self.orToken.join(self.parse_condition(c) for c in condition)
        elif isinstance(condition, ConditionNOT):
            return self.notToken + self.parse_condition(condition.item)
        elif isinstance(condition, ConditionNULLValue):
            return self.nullExpression % condition.item
        elif isinstance(condition, ConditionFieldEqualsValueExpression):
            return self.mapExpression % (condition.field, self.escape_value(condition.value))
        # Add more condition types as needed
        return "Unsupported condition type"

    def escape_value(self, value):
        """Escape special characters in values for Lucene query syntax."""
        if isinstance(value, str):
            return self.reEscape.sub(r"\\\1", value)
        return value

    def finalize_query(self, query):
        # Optionally finalize the query to fit LogRhythm's expected input
        return f"Final LogRhythm Query: {query}"

