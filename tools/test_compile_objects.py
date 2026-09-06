import copy
import json
import unittest
from pathlib import Path
from compile_objects import compile_objects

ROOT = Path(__file__).resolve().parents[1]


class ObjectsTest(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'SCOSWAMP/JSON/OBJECTS.json').read_text())

    def test_exact_existing_catalogues_and_reordered_rows(self):
        self.data['objects'].reverse()
        for lang, text in compile_objects(self.data, 16).items():
            self.assertEqual(text.encode('ascii'), (ROOT / f'SCOSWAMP/TEXT{lang}/OBJ{lang}.TXT').read_bytes())

    def test_reject_invalid_catalogues(self):
        mutations = [
            lambda d: d['objects'][1].update(id='ANNEAU'),
            lambda d: d['objects'][1].update(bit=0),
            lambda d: d['objects'][1].update(bit=17),
            lambda d: d['objects'][1].update(hidden=True),
            lambda d: d['objects'][1]['labels'].update(FR='Deux\nlignes'),
            lambda d: d['objects'][1]['labels'].pop('EN'),
        ]
        for mutate in mutations:
            data = copy.deepcopy(self.data)
            mutate(data)
            with self.assertRaises(ValueError):
                compile_objects(data, 16)

    def test_backend_capacity_is_explicit(self):
        data = {'schema': 1, 'objects': [
            {'id': f'ITEM{i}', 'bit': i, 'hidden': False,
             'labels': {'FR': f'Objet {i}', 'EN': f'Item {i}'}}
            for i in range(17)
        ]}
        self.assertEqual(len(compile_objects(data, 32)['FR'].splitlines()), 17)
        with self.assertRaises(ValueError):
            compile_objects(data, 16)


if __name__ == '__main__':
    unittest.main()
