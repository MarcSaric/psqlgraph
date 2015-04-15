import unittest
import logging
import uuid
from psqlgraph import Node, Edge, PsqlGraphDriver
from psqlgraph import PolyNode

host = 'localhost'
user = 'test'
password = 'test'
database = 'automated_test'
g = PsqlGraphDriver(host, user, password, database)

logging.basicConfig(level=logging.INFO)

from models import Test


class TestPsqlGraphDriver(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.g = g
        self.parent_id = str(uuid.uuid4())
        self.g.node_insert(PolyNode(self.parent_id, 'test'))
        self._create_subtree(self.parent_id)
        self.lone_id = str(uuid.uuid4())
        self.g.node_insert(PolyNode(self.lone_id, 'test'))

    def _create_subtree(self, parent_id, level=0):
        for i in range(4):
            node_id = str(uuid.uuid4())
            self.g.node_merge(
                node_id=node_id, label='test_{}'.format(level),
                properties={
                    'level': i, 'isTest': True, 'null': None})
            self.g.edge_insert(Edge(
                src_id=parent_id, dst_id=node_id, label='test'))
            if level < 2:
                self._create_subtree(node_id, level+1)

    def tearDown(self):
        self.g.engine.dispose()
        self._clear_tables()

    def _clear_tables(self):
        conn = self.g.engine.connect()
        conn.execute('commit')
        conn.execute('delete from edges')
        conn.execute('delete from nodes')
        conn.execute('delete from voided_nodes')
        conn.execute('delete from voided_edges')
        conn.close()

    def test_ids(self):
        with self.g.session_scope():
            self.assertTrue(self.g.nodes().ids(self.lone_id).one()
                            .node_id == self.lone_id)

    def test_not_ids(self):
        with self.g.session_scope():
            for n in self.g.nodes().not_ids(self.lone_id).all():
                self.assertTrue(n.node_id != self.lone_id)

    def test_has_edges(self):
        with self.g.session_scope():
            for n in self.g.nodes():
                self.assertTrue(self.g.nodes().ids(n.node_id).has_edges)

    def test_has_no_edges(self):
        with self.g.session_scope():
            n = self.g.nodes().ids(self.lone_id).one()
            self.assertTrue(self.g.nodes().ids(n.node_id).has_no_edges)

    def test_labels(self):
        with self.g.session_scope():
            for i in range(3):
                label = 'test'
                ns = self.g.nodes().labels(label).all()
                self.assertTrue(ns != [])
                for n in ns:
                    self.assertTrue(n.label == label)

    def test_not_labels(self):
        with self.g.session_scope():
            for i in range(3):
                label = 'test'
                ns = self.g.nodes().not_labels(label).all()
                self.assertTrue(ns != [])
                for n in ns:
                    self.assertTrue(n.label != label)

    def test_props(self):
        with self.g.session_scope():
            for i in range(3):
                ns = self.g.nodes().props({'level': i, 'isTest': True}).all()
                self.assertNotEqual(ns, [])
                for n in ns:
                    self.assertEqual(n['level'], i)
                    self.assertEqual(n['isTest'], True)

    def test_not_props(self):
        with self.g.session_scope():
            for i in range(3):
                ns = self.g.nodes().not_labels('test')\
                                   .not_props({'level': i, 'isTest': True})\
                                   .all()
                self.assertNotEqual(ns, [])
                for n in ns:
                    self.assertNotEqual(n['level'], i)
                    self.assertEqual(n['isTest'], True)

    def test_null_props(self):
        with self.g.session_scope():
            ns = self.g.nodes().not_labels('test')\
                               .null_props(['null'])\
                               .all()
            self.assertNotEqual(ns, [])
            for n in ns:
                self.assertFalse(n['null'])

    def test_path_out(self):
        with self.g.session_scope():
            n = self.g.nodes().path_out(['test_0', 'test_1', 'test_2']).one()
            self.assertEqual(n.node_id, self.parent_id)
            ns = self.g.nodes().path_out(['test_1', 'test_2']).all()
            self.assertNotEqual(ns, [])
            for n in ns:
                self.assertEqual(n.label, 'test_0')

    def test_empty_path_out(self):
        with self.g.session_scope():
            self.assertFalse(self.g.nodes().path_out(
                ['test_0', 'test_2']).all())

    def test_path_in(self):
        with self.g.session_scope():
            ns = self.g.nodes().path_in(['test_1', 'test_0']).all()
            self.assertNotEqual(ns, [])
            for n in ns:
                self.assertEqual(n.label, 'test_2')

    def test_empty_path_in(self):
        with self.g.session_scope():
            self.assertFalse(self.g.nodes().path_in(
                ['test_0', 'test_2']).all())

    def test_path_end(self):
        with self.g.session_scope():
            ns = self.g.nodes().path_end(['test_1', 'test_0']).all()
            self.assertNotEqual(ns, [])
            for n in ns:
                self.assertEqual(n.label, 'test_0')

    def test_ids_path_end(self):
        with self.g.session_scope():
            ns = self.g.nodes().ids_path_end(self.parent_id, ['test_0']).all()
            self.assertNotEqual(ns, [])
            for n in ns:
                self.assertEqual(n.label, 'test_0')
                self.assertNotEqual(n.node_id, self.parent_id)
