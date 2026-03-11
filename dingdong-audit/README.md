# 叮咚猫AI活力审计系统

轻量级企业AI活力感知系统，自动扫描AI调用日志，发现僵尸AI、边缘AI、卡顿AI和核心AI。

## 特性
- **本地部署**：数据不出客户服务器
- **代码开源**：可审计、可验证（MIT许可证）
- **元数据分析**：只读调用元数据，不触及业务内容
- **可追溯报告**：附带原始数据片段和分析脚本

## 快速开始

### 使用 Docker（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/nengyu-tech/dingdong-audit
cd dingdong-audit

# 2. 准备你的日志目录（或使用内置示例）
cp -r fake_logs logs

# 3. 使用 docker-compose 一键运行
docker-compose up

# 4. 查看生成的报告
ls reports/