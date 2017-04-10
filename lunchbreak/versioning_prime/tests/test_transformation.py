from itertools import permutations

from ..transformation import Transformation
from .serializers import TestField, TestSerializer
from .testcase import VersioningPrimeTestCase


class TestTransformation090(Transformation):

    bases = []
    version = '0.9.0'


class TestTransformation100(Transformation):

    bases = []
    version = '1.0.0'


class TestTransformation101(Transformation):

    bases = []
    version = '1.0.1'


class TransformationTestCase(VersioningPrimeTestCase):

    def test_for_field(self):
        transformation = TestTransformation100(
            base=TestField()
        )
        self.assertTrue(transformation.for_field)
        self.assertFalse(transformation.for_serializer)
        self.assertFalse(transformation.for_specific_field)

    def test_for_serializer(self):
        transformation = TestTransformation100(
            base=TestSerializer()
        )
        self.assertFalse(transformation.for_field)
        self.assertTrue(transformation.for_serializer)
        self.assertFalse(transformation.for_specific_field)

    def test_for_specific_field(self):
        transformation = TestTransformation100(
            base=TestSerializer(),
            field=TestField()
        )
        self.assertFalse(transformation.for_field)
        self.assertFalse(transformation.for_serializer)
        self.assertTrue(transformation.for_specific_field)

    def test_sorting(self):
        field101 = TestTransformation101(
            base=TestField()
        )
        field100 = TestTransformation100(
            base=TestField()
        )
        field090 = TestTransformation090(
            base=TestField()
        )

        serializer101 = TestTransformation101(
            base=TestSerializer()
        )
        serializer100 = TestTransformation100(
            base=TestSerializer()
        )
        serializer090 = TestTransformation090(
            base=TestSerializer()
        )

        specific_field101 = TestTransformation101(
            base=TestSerializer(),
            field=TestField()
        )
        specific_field100 = TestTransformation100(
            base=TestSerializer(),
            field=TestField()
        )
        specific_field090 = TestTransformation090(
            base=TestSerializer(),
            field=TestField()
        )

        perms = permutations(
            [
                serializer090,
                serializer100,
                serializer101,
                specific_field090,
                specific_field100,
                specific_field101,
            ]
        )

        # Serializers and specific fields can be in the same transformer.
        for p in perms:
            permutation = list(p)
            permutation.sort()
            self.assertEqual(
                permutation,
                [
                    specific_field090,
                    serializer090,
                    specific_field100,
                    serializer100,
                    specific_field101,
                    serializer101,
                ]
            )

        # Fields cannot have specific fields and cannot be applied together with
        # serializer or specific fields.
        perms = permutations(
            [
                field101,
                field090,
                field100,
            ]
        )

        for p in perms:
            permutation = list(p)
            permutation.sort()
            self.assertEqual(
                permutation,
                [
                    field090,
                    field100,
                    field101,
                ]
            )
