# coding=utf-8
import json

from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.httputil import url_concat, HTTPHeaders

from handler.metabase import MetaBaseHandler
from service.data.hr.hr_wx_wechat import HrWxWechatDataService


class PermanentQRHandler(MetaBaseHandler):
    GET_TICKET_API = 'https://api.weixin.qq.com/cgi-bin/qrcode/create'
    GET_QR_IMG_API = 'https://mp.weixin.qq.com/cgi-bin/showqrcode'
    CACHE_KEY_FMT = 'WECAHT_PERMANENTQR_{wechat_id}'
    SCENE_STR_FMT = 'wechat_permanent_qr-{wechat_id}'

    def get_qr_img_url(self, ticket):
        qr_img_url = url_concat(self.GET_QR_IMG_API, dict(ticket=ticket))
        self.logger.debug('GET WECAHT PERMANENT QRIMG URL: %s' % qr_img_url)
        return qr_img_url

    def get_cache_key(self, wechat_id):
        return self.CACHE_KEY_FMT.format(wechat_id=wechat_id)

    def set_ticket_cache(self, ticket, wechat_id):
        self.application.redis.set(
            self.get_cache_key(wechat_id),
            ticket,
            40
        )

    @gen.coroutine
    def get(self, hr_wx_wecaht_id):
        """通过wecaht id 获取永久二维码
        微信文档地址: https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1443433542
        """
        wechat_id = int(hr_wx_wecaht_id)
        self.logger.debug('GET WECAHT PERMANENT QR: %s' % wechat_id)

        # 有缓存从缓存中获取
        cached_ticket = self.application.redis.get(self.get_cache_key(wechat_id))
        if cached_ticket:
            self.write(
                dict(
                    status=0,
                    permanent_qr=self.get_qr_img_url(cached_ticket)
                )
            )
            return

        wechat = yield HrWxWechatDataService().get_wechat(
            dict(id=wechat_id)
        )

        if not wechat:
            self.write(dict(
                status=1,
                message='WECHAT NOT FOUND'
            ))
            self.set_status(404)
            return

        ticket_url = url_concat(self.GET_TICKET_API, dict(access_token=wechat.access_token))
        data = dict(
            action_name="QR_LIMIT_SCENE",
            action_info={"scene": {"scene_str": self.SCENE_STR_FMT.format(wechat_id=wechat_id)}}
        )
        self.logger.debug('GET WECAHT PERMANENT TICKET URL: %s- %s' % (ticket_url, data))

        get_ticket_response = yield AsyncHTTPClient().fetch(
            ticket_url,
            method="POST",
            body=json.dumps(data),
            headers=HTTPHeaders({"Content-Type": "application/json"}),
            request_timeout=10
        )

        ticket = json.loads(get_ticket_response.body.decode('u8') or "").get('ticket')  # 微信端这个ticket　60s有效

        if not ticket:
            self.write(dict(
                status=1,
                message='GET TICKET FAILED'
            ))
            self.set_status(400)
            return

        self.set_ticket_cache(ticket, wechat_id)
        self.write(
            dict(
                status=0,
                permanent_qr=self.get_qr_img_url(ticket),
                message='success'
            )
        )
