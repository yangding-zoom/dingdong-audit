import os
import shutil
import jinja2
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    报告生成器：生成HTML审计报告及数据溯源包
    """

    def __init__(self, output_dir: str, template_dir: Optional[str] = None):
        self.output_dir = output_dir
        if template_dir is None:
            template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.template_dir = template_dir
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
        os.makedirs(output_dir, exist_ok=True)

    def generate(self, classification_result: Dict[str, Dict],
                 records_with_raw: Optional[List] = None,
                 report_name: Optional[str] = None) -> str:
        if report_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_name = f'report_{timestamp}.html'

        total_ai = len(classification_result)
        classification_counts = {}
        for ai, data in classification_result.items():
            cls = data['classification']
            classification_counts[cls] = classification_counts.get(cls, 0) + 1

        template_data = {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_ai': total_ai,
            'classification_counts': classification_counts,
            'classifications': classification_result,
        }

        template = self.env.get_template('report.html')
        html_content = template.render(**template_data)

        report_path = os.path.join(self.output_dir, report_name)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        if records_with_raw is not None:
            self._generate_traceability_package(classification_result, records_with_raw, report_name)

        return report_path

    def _generate_traceability_package(self, classification_result: Dict[str, Dict],
                                       records_with_raw: List, report_name: str):
        base_name = os.path.splitext(report_name)[0]
        package_dir = os.path.join(self.output_dir, f'{base_name}_溯源包')
        os.makedirs(package_dir, exist_ok=True)

        # logs_sample
        logs_sample_dir = os.path.join(package_dir, 'logs_sample')
        os.makedirs(logs_sample_dir, exist_ok=True)

        ai_raw_lines = {}
        for record, raw_line in records_with_raw:
            ai = record.get('ai_name')
            if not ai:
                continue
            if ai not in ai_raw_lines:
                ai_raw_lines[ai] = []
            if len(ai_raw_lines[ai]) < 5:
                ai_raw_lines[ai].append(raw_line)

        for ai, lines in ai_raw_lines.items():
            file_path = os.path.join(logs_sample_dir, f'{ai}.log')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

        # scripts
        scripts_dir = os.path.join(package_dir, 'scripts')
        os.makedirs(scripts_dir, exist_ok=True)

        import dingdong
        dingdong_path = os.path.dirname(dingdong.__file__)
        dst_path = os.path.join(scripts_dir, 'dingdong')
        shutil.copytree(dingdong_path, dst_path, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))

        req_src = os.path.join(os.path.dirname(dingdong_path), 'requirements.txt')
        if os.path.exists(req_src):
            shutil.copy2(req_src, scripts_dir)

        # run.log
        run_log_src = os.path.join(self.output_dir, 'run.log')
        if os.path.exists(run_log_src):
            shutil.copy2(run_log_src, package_dir)

        # README.md (使用列表拼接，避免三引号字符串可能引起的语法问题)
        readme_lines = [
            f"# 数据溯源包 - {base_name}",
            "",
            "本目录包含叮咚猫AI活力审计系统运行产生的原始数据和分析脚本，可用于手动验证报告结果。",
            "",
            "## 文件说明",
            "- `logs_sample/`：每个AI的前5条原始日志片段（脱敏）。",
            "- `scripts/`：本次分析使用的Python脚本（与开源仓库一致）。",
            "- `run.log`：叮咚猫本次运行的完整日志。",
            "",
            "## 手动验证步骤",
            "1. 确保已安装Python 3.8+ 和依赖（见 scripts/requirements.txt）。",
            "2. 进入 scripts/ 目录。",
            "3. 运行以下命令重新计算分类（假设日志文件位于 ../logs_sample/）：",
            "   ```bash",
            "   python -m dingdong.cli --log-dir ../logs_sample --report --output-dir ./verify_output",
            "   ```",
            "4. 对比新生成的报告与原始报告是否一致。",
            "",
            "注意：由于日志样本仅为前5条，结果可能与完整日志有差异。如需完整验证，请使用原始日志文件。"
        ]
        readme_content = "\n".join(readme_lines)

        readme_path = os.path.join(package_dir, 'README.md')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        logger.info("数据溯源包已生成: %s", package_dir)