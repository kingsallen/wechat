# coding=utf-8

from datetime import datetime

from mockito import *
from tornado.concurrent import Future
from tornado.testing import AsyncTestCase, gen_test
from tornado.util import ObjectDict

from service.page.user.sharechain import SharechainPageService
from util.common.log import Logger


class TestShareChainService(AsyncTestCase):
    def setUp(self):
        super().setUp()
        self.logger = Logger()
        self.service_to_test = SharechainPageService()

        self.future_false = Future()
        self.future_false.set_result(False)

        self.future_true = Future()
        self.future_true.set_result(True)

        self.future_int_123 = Future()
        self.future_int_123.set_result(123)

        self.future_parent_share_chain_record_depth_1 = Future()
        self.future_parent_share_chain_record_depth_1.set_result(
            ObjectDict({
                "id":                  1,
                "position_id":         2,
                "root_recom_user_id":  3,
                "root2_recom_user_id": 0,
                "recom_user_id":       3,
                "presentee_user_id":   6,
                "depth":               1,
                "parent_id":           0,
                "click_time":          datetime(2000, 1, 1),
                "create_time":         datetime(2000, 1, 1)
            })
        )

        self.future_parent_share_chain_record_depth_5 = Future()
        self.future_parent_share_chain_record_depth_5.set_result(
            ObjectDict({
                "id":                  1,
                "position_id":         2,
                "root_recom_user_id":  3,
                "root2_recom_user_id": 4,
                "recom_user_id":       5,
                "presentee_user_id":   6,
                "depth":               5,
                "parent_id":           10,
                "click_time":          datetime(2000, 1, 1),
                "create_time":         datetime(2000, 1, 1)
            })
        )

        self.future_hr_remark_record = Future()
        self.future_hr_remark_record.set_result(ObjectDict(hraccount_id=1))

    @gen_test
    def test_save_recom_return_zero_while_no_existed_record_return_false(self):
        dummy_last_share_record = ObjectDict(position_id=1)

        when(self.service_to_test)._no_existed_record(any()).thenReturn(
            self.future_false)

        ret = yield self.service_to_test._save_recom(
            dummy_last_share_record, 'dummy')

        self.assertEqual(0, ret)

    @gen_test
    def test_save_recom_presentee_is_employee_with_none_parent_id(self):
        dummy_last_share_record = ObjectDict(
            position_id=1,
            presentee_user_id=22,
            create_time=datetime(2000, 1, 1)
        )
        when(self.service_to_test)._no_existed_record(any()).thenReturn(
            self.future_true)
        when(self.service_to_test)._is_valid_employee(any(), any()).thenReturn(
            self.future_true)
        when(self.service_to_test.candidate_share_chain_ds).insert_share_chain(
            any()).thenReturn(self.future_int_123)

        ret = yield self.service_to_test._save_recom(
            last_share_record=dummy_last_share_record,
            share_chain_parent_id=None
        )
        self.assertEqual(123, ret)
        verify(self.service_to_test.candidate_share_chain_ds,
               times=1).insert_share_chain(any())

    @gen_test
    def test_save_recom_presentee_is_not_employee_with_none_parent_id(self):
        dummy_last_share_record = ObjectDict(
            position_id=1,
            presentee_user_id=22,
            recom_user_id=23,
            create_time=datetime(2000, 1, 1)
        )

        when(self.service_to_test)._no_existed_record(any()).thenReturn(
            self.future_true)
        when(self.service_to_test)._is_valid_employee(any(), any()).thenReturn(
            self.future_false)

        share_chain_ds = self.service_to_test.candidate_share_chain_ds
        when(share_chain_ds).insert_share_chain(any()).thenReturn(
            self.future_int_123)

        when(self.service_to_test)._hr_remark_ignored_record(any()).thenReturn(
            self.future_hr_remark_record)

        remark_ds = self.service_to_test.candidate_remark_ds
        when(remark_ds).update_candidate_remark(fields=any(),
                                                conds=any()).thenReturn(
            self.future_true)

        ret = yield self.service_to_test._save_recom(
            last_share_record=dummy_last_share_record,
            share_chain_parent_id=None
        )
        self.assertEqual(123, ret)
        verify(self.service_to_test.candidate_share_chain_ds,
               times=1).insert_share_chain(any())

    @gen_test
    def test_save_recom_presentee_is_not_employee_with_valid_parent_id(self):
        dummy_last_share_record = ObjectDict(
            position_id=1,
            presentee_user_id=22,
            recom_user_id=23,
            create_time=datetime(2000, 1, 1)
        )

        when(self.service_to_test)._no_existed_record(any()).thenReturn(
            self.future_true)
        when(self.service_to_test)._is_valid_employee(any(), any()).thenReturn(
            self.future_false)

        share_chain_ds = self.service_to_test.candidate_share_chain_ds
        when(share_chain_ds).get_share_chain({'id': 101}).thenReturn(
            self.future_parent_share_chain_record_depth_5)

        when(share_chain_ds).insert_share_chain({
            "position_id":         dummy_last_share_record.position_id,
            "presentee_user_id":   dummy_last_share_record.presentee_user_id,
            "recom_user_id":       dummy_last_share_record.recom_user_id,
            "root_recom_user_id":  3,
            "root2_recom_user_id": 4,
            "click_time":          dummy_last_share_record.create_time,
            "depth":               5 + 1,
            "parent_id":           101
        }).thenReturn(self.future_int_123)

        when(self.service_to_test)._hr_remark_ignored_record(any()).thenReturn(
            self.future_hr_remark_record)
        remark_ds = self.service_to_test.candidate_remark_ds
        when(remark_ds).update_candidate_remark(
            fields=any(), conds=any()).thenReturn(self.future_true)

        ret = yield self.service_to_test._save_recom(
            last_share_record=dummy_last_share_record,
            share_chain_parent_id=101)

        self.assertEqual(123, ret)
        verify(self.service_to_test.candidate_share_chain_ds,
               times=1).insert_share_chain(any())

    @gen_test
    def test_get_referral_employee_user_id(self):
        # todo tangyiliang
        pass

    @gen_test
    def test_is_employee_presentee(self):
        # todo tangyiliang
        pass
