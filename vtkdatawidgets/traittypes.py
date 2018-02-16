
import sys

from traitlets import Container, TraitError, class_of

class VarTuple(Container):
    klass = tuple
    _cast_types = (list, set)

    def __init__(self, trait=None, default_value=None, minlen=0, maxlen=sys.maxsize, **kwargs):
        """Create a variable length tuple trait type from a list, set, or tuple.

        The default value is created by doing ``tuple(default_value)``,
        which creates a copy of the ``default_value``.

        ``trait`` can be specified, which restricts the type of elements
        in the container to that TraitType.

        If only one arg is given and it is not a Trait, it is taken as
        ``default_value``:

        ``c = VarTuple([1, 2, 3])``

        Parameters
        ----------

        trait : TraitType [ optional ]
            the type for restricting the contents of the Container.
            If unspecified, types are not checked.

        default_value : SequenceType [ optional ]
            The default value for the Trait.  Must be list/tuple/set, and
            will be cast to the container type.

        minlen : Int [ default 0 ]
            The minimum length of the tuple

        maxlen : Int [ default sys.maxsize ]
            The maximum length of the tuple
        """
        self._minlen = minlen
        self._maxlen = maxlen
        super(VarTuple, self).__init__(trait=trait, default_value=default_value,
                                       **kwargs)

    def length_error(self, obj, value):
        e = "The '%s' trait of %s instance must be of length %i <= L <= %i, but a value of %s was specified." \
            % (self.name, class_of(obj), self._minlen, self._maxlen, value)
        raise TraitError(e)

    def validate_elements(self, obj, value):
        length = len(value)
        if length < self._minlen or length > self._maxlen:
            self.length_error(obj, value)

        return super(VarTuple, self).validate_elements(obj, value)

    def validate(self, obj, value):
        value = super(VarTuple, self).validate(obj, value)
        value = self.validate_elements(obj, value)
        return value