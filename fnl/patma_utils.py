"""
Useful matching classes for context-manager-patma
"""
from collections.abc import Sequence
from context_manager_patma import register


@register("Cons")
class Cons:
    """Patter-match on the first element of a sequence and the rest of them"""
    @staticmethod
    def __match__(subpatterns, value, debug):
        if len(subpatterns) != 2:
            raise ValueError(f"Expected 2 subpatterns, got {len(subpatterns)}")

        if not isinstance(value, Sequence):
            return None

        if len(value) < 2:
            return None

        first_pattern, rest_pattern = subpatterns

        if (first := first_pattern.match(value[0], debug)) is None:
            return None

        if (rest := rest_pattern.match(value[1:], debug)) is None:
            return None

        return {**first, **rest}


@register("Seq")
class Seq:
    @staticmethod
    def __match__(subpatterns, value, debug):
        if not isinstance(value, Sequence):
            return None

        if len(subpatterns) != len(value):
            return None

        matched = {}
        for (pattern, element) in zip(subpatterns, value):
            if (submatch := pattern.match(element, debug)) is None:
                return None
            matched.update(submatch)
        return matched


@register("Pi")
class Pi:
    """
    Intersection pattern

    Can  be used to create aliases, for example:
        Pi(elements, Sexpr())  <-- Sexpr() matches any s-expression
    """
    @staticmethod
    def __match__(subpatterns, value, debug):
        matched = {}
        for pattern in subpatterns:
            if (submatch := pattern.match(value, debug)) is None:
                return None
            matched.update(submatch)
        return matched
