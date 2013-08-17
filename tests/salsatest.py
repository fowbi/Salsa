import unittest
import os
from salsa import Config, Salsa_Share
from salsa.exceptions import SalsaException, SalsaConnectionException


class SalsaTest(unittest.TestCase):
    def setUp(self):
        TEST_CONFIG = """name: share1
username: user_1
password: user_1_pass
server: 1.1.1.1
share: share
mount_point: share_test
---
name: share2
username: guest
password:
server: 1.1.1.1
share: share2
mount_point: share_test_2"""

        f = open('/tmp/salsa_config', 'w+')
        f.write(TEST_CONFIG)
        f.close()

        self.config = Config('/tmp/salsa_config')
        self.config.load()

    def testLoadingConfig(self):
        self.assertEqual(len(self.config.shares), 2)
        for share in self.config.shares:
            self.assertIsInstance(share, Salsa_Share)
            self.assertEqual(share.server, '1.1.1.1')

    def testAddShare(self):
        ss = Salsa_Share('share3', '3.3.3.3')
        ss.username = 'user_2'
        ss.password = 'user_2_pass'
        ss.share = 'share_3'
        ss.mount_point = 'share_test_3'
        self.config.add_share(ss)

        # Reload config
        config_ = Config('/tmp/salsa_config')
        config_.load()
        self.assertEqual(len(config_.shares), 3)

    def testAddShareWithEmptyUsername(self):
        ss = Salsa_Share('share3', '3.3.3.3')
        ss.username = ''
        ss.password = 'user_2_pass'
        ss.share = 'share_3'
        ss.mount_point = 'share_test_3'
        self.config.add_share(ss)

        # Reload config
        config_ = Config('/tmp/salsa_config')
        config_.load()
        self.assertEqual(len(config_.shares), 3)

        for share in self.config.shares:
            if share.name == 'share_3':
                self.assertEqual(share.username, 'guest')
                self.assertEqual(share.password, '')

    def testAddDuplicateShareName(self):
        ss = Salsa_Share('share1', '1.1.1.1')
        ss.username = 'user_2'
        ss.password = 'user_2_pass'
        ss.share = 'share_3'
        ss.mount_point = 'share_test_3'
        self.assertRaises(SalsaException, self.config.add_share, ss)

    def testDeleteShare(self):
        self.config.delete_share('share1')

        # Reload config
        config_ = Config('/tmp/salsa_config')
        config_.load()
        self.assertEqual(len(config_.shares), 1)

    def testDeleteUnkownShare(self):
        self.assertRaises(SalsaException, self.config.delete_share, 'share3')

        # Reload config
        config_ = Config('/tmp/salsa_config')
        config_.load()
        self.assertEqual(len(config_.shares), 2)

    def testEditShare(self):
        ss = Salsa_Share('share1_4', '1.1.1.1')
        ss.username = ''
        ss.password = 'user_2_pass'
        ss.share = 'share_3'
        ss.mount_point = 'share_test_3'

        self.config.edit_share('share1', ss)

        # Reload config
        config_ = Config('/tmp/salsa_config')
        config_.load()
        self.assertEqual(len(config_.shares), 2)

        for share in config_.shares:
            if share.name == 'share1_4':
                self.assertEqual(share.username, 'guest')
                self.assertEqual(share.password, '')

    def testEditUnkownShare(self):
        ss = Salsa_Share('share1_4', '1.1.1.1')
        ss.username = ''
        ss.password = 'user_2_pass'
        ss.share = 'share_3'
        ss.mount_point = 'share_test_3'
        self.assertRaises(Exception, self.config.edit_share, ('testt', ss))

    def testSuccesfulShareMount(self):
        pass

    def testSuccesfulShareUnmount(self):
        pass

    def testUnsuccesfulShareMount(self):
        config_ = Config('/tmp/salsa_config')
        config_.load()
        self.assertRaises(
            SalsaConnectionException,
            config_.mount_share,
            'share1')

    def testUnsuccesfulShareUnmount(self):
        config_ = Config('/tmp/salsa_config')
        config_.load()
        self.assertRaises(
            SalsaConnectionException,
            config_.umount_share,
            'share1')

    def tearDown(self):
        os.unlink('/tmp/salsa_config')


if __name__ == '__main__':
    unittest.main()
