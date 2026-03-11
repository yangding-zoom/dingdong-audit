import os
import threading
import time
import logging
import tempfile
import zipfile
from flask import Flask, render_template, request, jsonify, send_file, abort
from ..config import load_config, save_config, DEFAULT_CONFIG
from ..runner import run_scan

# 配置日志（避免与root logger冲突）
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-change-in-production'

# 添加时间过滤器，用于模板中的 datetimeformat
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    """将时间戳（秒）转换为指定格式的字符串"""
    from datetime import datetime
    return datetime.fromtimestamp(value).strftime(format)

# 简单任务状态存储（仅适用于单进程开发，生产需用外部存储）
scan_tasks = {}

def async_scan(log_dir, output_dir, thresholds, task_id):
    try:
        report_path = run_scan(log_dir, output_dir, thresholds)
        scan_tasks[task_id] = {'status': 'completed', 'report_path': report_path}
        logger.info(f"任务 {task_id} 完成，报告: {report_path}")
    except Exception as e:
        scan_tasks[task_id] = {'status': 'failed', 'error': str(e)}
        logger.error(f"任务 {task_id} 失败: {e}")

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/config', methods=['GET', 'POST'])
def config_page():
    if request.method == 'POST':
        new_config = {
            'log_dir': request.form['log_dir'],
            'output_dir': request.form['output_dir'],
            'thresholds': {
                'zombie_days': int(request.form['zombie_days']),
                'edge_call_threshold': int(request.form['edge_call_threshold']),
                'edge_dept_threshold': int(request.form['edge_dept_threshold']),
                'slow_threshold': float(request.form['slow_threshold']),
                'error_threshold': float(request.form['error_threshold']),
                'core_call_threshold': int(request.form['core_call_threshold']),
                'core_dept_threshold': int(request.form['core_dept_threshold']),
            }
        }
        save_config(new_config)
        return render_template('config.html', config=new_config, saved=True)
    config = load_config()
    return render_template('config.html', config=config, saved=False)

@app.route('/scan', methods=['GET', 'POST'])
def scan_page():
    if request.method == 'POST':
        config = load_config()
        log_dir = config['log_dir']
        output_dir = config['output_dir']
        thresholds = config.get('thresholds')
        task_id = str(int(time.time()))
        scan_tasks[task_id] = {'status': 'started'}
        thread = threading.Thread(target=async_scan, args=(log_dir, output_dir, thresholds, task_id))
        thread.daemon = True
        thread.start()
        return jsonify({'task_id': task_id})
    return render_template('scan.html')

@app.route('/scan/status/<task_id>')
def scan_status(task_id):
    task = scan_tasks.get(task_id)
    if task is None:
        return jsonify({'status': 'not_found'})
    return jsonify(task)

@app.route('/reports')
def reports_list():
    config = load_config()
    output_dir = config['output_dir']
    reports = []
    if os.path.exists(output_dir):
        for fname in os.listdir(output_dir):
            if fname.endswith('.html'):
                report_path = os.path.join(output_dir, fname)
                mtime = os.path.getmtime(report_path)
                trace_dir = os.path.join(output_dir, fname.replace('.html', '_溯源包'))
                reports.append({
                    'name': fname,
                    'path': fname,
                    'time': mtime,
                    'has_trace': os.path.exists(trace_dir)
                })
    reports.sort(key=lambda x: x['time'], reverse=True)
    return render_template('reports.html', reports=reports)

@app.route('/report/<path:filename>')
def view_report(filename):
    config = load_config()
    output_dir = config['output_dir']
    file_path = os.path.join(output_dir, filename)
    if not os.path.exists(file_path) or not filename.endswith('.html'):
        abort(404)
    return send_file(file_path)

@app.route('/trace/<path:dirname>')
def download_trace(dirname):
    config = load_config()
    output_dir = config['output_dir']
    trace_dir = os.path.join(output_dir, dirname)
    if not os.path.isdir(trace_dir):
        abort(404)
    # 创建临时zip
    temp = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    with zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(trace_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, trace_dir)
                zf.write(file_path, arcname)
    temp.close()
    return send_file(temp.name, as_attachment=True, download_name=f'{dirname}.zip', mimetype='application/zip')