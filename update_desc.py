# -*- coding: utf-8 -*-
"""update_desc.py — 签到后统计各账号成长值/容量并自动更新仓库简介
CI 中运行，依赖环境变量 ADMIN_PAT + COOKIE_QUARK（仓库 Secrets）
只查询不签到，签到由主脚本完成
"""
import json
import os
import re
import subprocess
import time

from checkIn_Quark import Quark

REPO_API = 'https://api.github.com/repos/XXXGITHUB777/Quark_Auot_Check_In'


def main():
    pat = os.environ.get('ADMIN_PAT', '')
    cookies = os.environ.get('COOKIE_QUARK', '')
    if not pat or not cookies:
        print('未设置 ADMIN_PAT 或 COOKIE_QUARK，跳过简介更新')
        return

    cookie_list = re.split('\n|&&', cookies)
    parts = []
    for i, ck in enumerate(cookie_list, 1):
        if not ck.strip():
            continue
        try:
            user_data = {}
            for a in ck.replace(' ', '').split(';'):
                if a and '=' in a:
                    user_data.update({a[:a.index('=')]: a[a.index('=') + 1:]})
            q = Quark(user_data)
            info = q.get_growth_info()
            if info:
                growth = info.get('_growth', '?')
                total_cap = info.get('_total_capacity', 0)
                cap_str = q.convert_bytes(total_cap) if total_cap else '?'
                parts.append('账号{} 成长{} 容量{}'.format(i, growth, cap_str))
                print('  账号{}: 成长 {} 容量 {}'.format(i, growth, cap_str))
            else:
                parts.append('账号{} 查询失败'.format(i))
        except Exception as e:
            parts.append('账号{} 查询失败'.format(i))
            print('  账号{} 查询失败: {}'.format(i, str(e)[:60]))

    today = time.strftime('%Y-%m-%d')
    desc = '夸克网盘自动签到领空间 | {}（{}更新）| CI 11:53+13:07'.format(
        ' / '.join(parts), today)

    r = subprocess.run(['curl', '-s', '--max-time', '20', '-X', 'PATCH',
        '-H', 'Authorization: Bearer ' + pat,
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({'description': desc}),
        REPO_API], capture_output=True, text=True)
    try:
        resp = json.loads(r.stdout)
        print('简介已更新:', resp.get('description'))
    except Exception:
        print('简介更新失败:', r.stdout[:100])


if __name__ == '__main__':
    main()
