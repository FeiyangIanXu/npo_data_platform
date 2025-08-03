# xml_parser_poc.py (V16 - 真相版)

import subprocess
import json
import logging
import requests
import pandas as pd
from io import StringIO
import os
from datetime import datetime

# --- 配置区 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 这是从你上传的 R 脚本中找到的、正确的 URL 格式。
# 它直接从 AWS S3 存储桶下载索引。
INDEX_BASE_URL = "https://s3.amazonaws.com/irs-form-990/"

# --- 函数定义区 ---

def get_latest_index_dataframe() -> pd.DataFrame:
    """
    直接从 AWS S3 下载最新的年度索引文件。
    它会从当前年份开始，一直往回找，直到找到一个有效的索引文件为止。
    """
    current_year = datetime.now().year
    # 我们会检查今年以及过去5年
    for year in range(current_year, current_year - 6, -1):
        index_filename = f"index_{year}.csv"
        index_url = f"{INDEX_BASE_URL}{index_filename}"
        
        logging.info(f"正在尝试从以下地址下载索引: {index_url}")
        try:
            response = requests.get(index_url, timeout=30)
            # 在 S3 上，403 或 404 错误意味着文件不存在，这对于未来的年份是正常情况。
            if response.status_code == 200:
                logging.info(f"成功！已找到并下载 {year} 年的索引。")
                index_content = StringIO(response.text)
                df = pd.read_csv(index_content)
                return df
            else:
                logging.warning(f"未找到 {year} 年的索引 (状态码: {response.status_code})。正在尝试前一年。")
        except requests.exceptions.RequestException as e:
            logging.error(f"下载 {index_url} 时发生网络错误: {e}")
            # 如果发生网络错误，则停止尝试
            return None
            
    logging.error("在过去5年中未能找到一个有效的索引文件。")
    return None

# --- 主程序执行区 ---
if __name__ == "__main__":
    print("====== IRS 990 数据采集器 (V16 - 真相版) ======")
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    parser_folder = os.path.join(project_root, 'form-990-xml-parser')
    parser_script_path = os.path.join(parser_folder, 'XML_Parser.py')
    parser_python_executable = os.path.join(parser_folder, 'parser-venv', 'Scripts', 'python.exe')

    if not os.path.exists(parser_python_executable) or not os.path.exists(parser_script_path):
        print("❌ 严重错误: 解析器工具或其环境未找到。请确保项目设置正确。")
    else:
        # 1. 直接从 AWS S3 获取最新的索引
        index_df = get_latest_index_dataframe()
        
        if index_df is not None and not index_df.empty:
            # 2. 从数据框中随机获取一个 OBJECT_ID
            random_filing = index_df.sample(n=1).iloc[0]
            object_id = str(random_filing.get('OBJECT_ID'))
            
            logging.info(f"已随机选择一个文件进行处理。OBJECT_ID: {object_id}")

            try:
                # 3. 调用外部解析器工具
                command = [parser_python_executable, parser_script_path, object_id]
                result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
                
                parsed_json = json.loads(result.stdout)
                data = parsed_json[0]

                print("\n✅ 成功！已从外部解析器工具收到数据:")
                print("==========================================================")
                print(f"  组织名称: {data.get('filer_name')}")
                print(f"  税号 (EIN):      {data.get('ein')}")
                print(f"  报税年份:          {data.get('tax_year')}")
                print(f"  总收入:     ${data.get('total_revenue'):,}")
                print(f"  总支出:    ${data.get('total_expenses'):,}")
                print("==========================================================")
                print("\n🏆🏆🏆 正确的数据管道终于成功运行！")

            except subprocess.CalledProcessError as e:
                logging.error("外部解析器脚本执行失败。")
                logging.error(f"错误输出: {e.stderr}")
            except Exception as e:
                logging.error(f"发生未知错误: {e}")