from flask import Flask, render_template_string
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# 生成模拟数据
def generate_mock_data():
    ais = []
    names = ['小悬', '投资型幼苗', '老树', '卡顿同学', '边缘1', '边缘2', '核心AI', '僵尸1', '僵尸2']
    for name in names:
        calls = random.choice([0, 0, 5, 20, 150, 300, 0, 0, 1])
        last_call = datetime.now() - timedelta(days=random.choice([1, 5, 10, 30, 60, 90]))
        depts = random.sample(['研发', '销售', '市场', '客服', '财务'], k=random.randint(1,3))
        error_rate = round(random.uniform(0, 0.1), 4)
        avg_time = round(random.uniform(0.1, 6.0), 2)

        if calls == 0 or (datetime.now() - last_call).days > 30:
            status = '僵尸AI'
        elif calls < 10 and len(depts) == 1:
            status = '边缘AI'
        elif error_rate > 0.05 or avg_time > 5:
            status = '卡顿AI'
        elif calls > 100 and len(depts) > 2:
            status = '核心AI'
        else:
            status = '正常'

        ais.append({
            'name': name,
            'calls': calls,
            'last_call': last_call.strftime('%Y-%m-%d'),
            'departments': ', '.join(depts),
            'error_rate': f'{error_rate:.2%}',
            'avg_time': avg_time,
            'status': status
        })
    return ais

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>叮咚猫 · AI活力审计</title>
    <style>
        body { font-family: Arial; margin: 20px; background: #f5f5f5; }
        h1 { color: #2c3e50; }
        table { border-collapse: collapse; width: 100%; background: white; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
        .zombie { background-color: #ffcccc; }
        .edge { background-color: #ffffcc; }
        .core { background-color: #ccffcc; }
        .stuck { background-color: #ffcc99; }
    </style>
</head>
<body>
    <h1>🔍 叮咚猫 AI活力审计报告</h1>
    <p>生成时间: {{ now }}</p>
    <table>
        <tr>
            <th>AI名称</th><th>调用次数(30天)</th><th>最后调用</th><th>涉及部门</th><th>错误率</th><th>平均响应(秒)</th><th>状态</th>
        </tr>
        {% for ai in ais %}
        <tr class="{% if ai.status == '僵尸AI' %}zombie{% elif ai.status == '边缘AI' %}edge{% elif ai.status == '核心AI' %}core{% elif ai.status == '卡顿AI' %}stuck{% endif %}">
            <td>{{ ai.name }}</td>
            <td>{{ ai.calls }}</td>
            <td>{{ ai.last_call }}</td>
            <td>{{ ai.departments }}</td>
            <td>{{ ai.error_rate }}</td>
            <td>{{ ai.avg_time }}</td>
            <td><strong>{{ ai.status }}</strong></td>
        </tr>
        {% endfor %}
    </table>
    <p>注：本报告基于模拟数据，真实环境需接入日志。</p>
</body>
</html>
'''

@app.route('/')
def index():
    ais = generate_mock_data()
    return render_template_string(HTML_TEMPLATE, ais=ais, now=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
