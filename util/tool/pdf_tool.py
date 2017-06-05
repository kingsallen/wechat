# coding=utf-8

# @Time    : 3/22/17 17:21
# @Author  : panda (panyuxin@moseeker.com)
# @File    : pdf_tool.py
# @DES     :

import os
from tornado import template

from setting import settings
from util.tool.url_tool import make_static_url
from util.tool.str_tool import to_str

resume_tpath = os.path.join(settings.template_path, 'refer/weixin/application/')

def save_file(spath, sname, content):
    """
    存储文件的通用方法
    :param spath:  存储文件路径
    :param sname:  存储文件名
    :param content: 存储内容
    :return:
    """
    with open(os.path.join(spath, sname), "w", encoding="utf-8") as f:
        f.write(to_str(content))
        f.close()

def get_render_resume_content(resume, template_others, dict_conf):
    '''
    :parameter resume 简历名
    模板填充, 使用与被finish掉之后使用
    '''

    loader = template.Loader(resume_tpath)
    return loader.load("resume2pdf_neoweixin.html").generate(
        resume=resume,
        template_others=template_others,
        static_url=make_static_url,
        const=dict_conf)

def save_application_file(resume, save_html_fname, template_others, savepath, dict_conf):
    """
    存储申请的通用文件名,HR和mtp的申请通用,谨慎修改
    该方法将模板填充,生成同名的pdf文件
    :param resume:
    :param save_html_fname:
    :param template_others:
    :param savepath:
    :param dict_conf:
    :return:
    """

    fd = get_render_resume_content(resume, template_others, dict_conf)
    save_file(savepath, save_html_fname, fd)

def get_create_pdf_by_html_cmd(html_fname, pdf_fname):
    """
    :param html_fname:
    :param pdf_fname:
    :return:
    """
    return "xvfb-run -a -s '-screen 0 640x480x16' wkhtmltopdf %s %s" % (
        html_fname, pdf_fname)

def generate_html_template_resume(employee, conf, profile, template_others, position, dict_conf):
    """
    申请后发送给hr简历的邮件模板
    :param employee:
    :param conf:
    :param profile:
    :param template_others:
    :param position:
    :return:
    """
    loader = template.Loader(resume_tpath)
    return loader.load("email_resume_template_new.html").generate(
        resume=profile,
        template_others=template_others,
        position=position,
        employee=employee,
        conf=conf,
        const=dict_conf,
        static_url=make_static_url,
        pc=settings.pc_host)

def generate_resume_for_hr(profile,template_others,dict_conf,position,real_company_info):
    import datetime
    year=datetime.date.today().year
    loader = template.Loader(resume_tpath)
    body=loader.load("resume_inform_hr.html").generate(resume=profile,
        template_others=template_others,
        const=dict_conf,
        position=position,
        real_company_info=real_company_info,
        year=year)
    return body

