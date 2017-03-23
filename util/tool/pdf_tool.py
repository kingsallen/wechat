# coding=utf-8

# @Time    : 3/22/17 17:21
# @Author  : panda (panyuxin@moseeker.com)
# @File    : pdf_tool.py
# @DES     :

import os
from tornado import template

import conf.common as const
from setting import settings
from util.tool.url_tool import make_static_url

def save_file(spath, sname, content):
    '''
    存储文件的通用方法
    :param spath:  存储文件路径
    :param sname:  存储文件名
    :param content: 存储内容
    :return:
    '''
    with open(os.path.join(spath, sname), "w", "utf-8") as f:
        f.write(content)
        f.close()

def get_render_resume_content(template_path, template_name, resume, template_others, const):
    ''''
    :parameter template_path 路径
    :parameter template_name 名称
    :parameter resume 简历名
    模板填充, 使用与被finish掉之后使用
    '''
    if not template_path.endswith('/'):
        template_path += '/'
    loader = template.Loader(template_path)
    return loader.load(template_name).generate(
            resume=resume,
            template_others=template_others or {},
            static_url=make_static_url,
            const=const)


def save_application_file(template_path, template_name, resume, save_html_fname, template_others, savepath):
    '''
    存储申请的通用文件名,HR和mtp的申请通用,谨慎修改
    该方法将模板填充,生成同名的pdf文件
    :param template_path:
    :param static_url:
    :param resume:
    :param save_html_fname:
    :param template_others:
    :param savepath:
    :return:
    '''
    fd = get_render_resume_content(template_path, template_name, resume, template_others, make_static_url)
    save_file(savepath, save_html_fname, fd)


def get_create_pdf_by_html_cmd(html_fname, pdf_fname):
    '''
    :param html_fname:
    :param pdf_fnamee:
    :return:
    '''
    return "xvfb-run -a -s '-screen 0 640x480x16' wkhtmltopdf {hfile} {pfile}".format(hfile=html_fname, pfile=pdf_fname)

def generate_html_template_resume(employee, conf, profile, template_others, position):
    """
    申请后发送给hr简历的邮件模板
    :param self
    :param employee:
    :param conf:
    :param profile:
    :param template_others:
    :param position:
    :return:
    """
    loader = template.Loader(settings.template_path + "/neo_weixin/systemmessage/")
    return loader.load("email_resume_template_new.html").generate(
            resume=profile,
            template_others=template_others,
            position=position,
            employee=employee,
            conf=conf,
            const=const,
            static_url=make_static_url,
            pc=settings.pc_host)
