import requests
import json
import logging

# --- 配置区 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# V8 版：使用从官方文档 https://990data.givingtuesday.org/asset-bank/ 找到的、
# 经验证的 Base URL 和 Endpoints
BASE_URL = "https://990-infrastructure.gtdata.org/"

# 我们需要一个真实的、有数据的 EIN 来启动查询。
# 我们就用 Giving Tuesday 自己的 EIN 来测试。
TEST_EIN = "842929872"

def final_verify_api():
    """
    使用官方文档的最新信息，最终验证 Giving Tuesday API 的核心功能。
    """
    
    # --- 任务 1: 验证 efilexml 端点 (获取某个组织的所有原始文件链接) ---
    logging.info(f">>> 正在测试 'efilexml' 端点，查询 EIN: {TEST_EIN} 的文件列表...")
    endpoint = "irs-data/efilexml"
    params = {'ein': TEST_EIN}
    
    try:
        response = requests.get(BASE_URL + endpoint, params=params, timeout=30)
        
        if response.status_code == 200:
            logging.info(f"✅ 成功！'efilexml' 端点返回状态码: {response.status_code}")
            data = response.json()
            
            print("\n--- 'efilexml' 端点返回数据摘要 ---")
            if isinstance(data, list) and len(data) > 0:
                print(f"成功找到了 {len(data)} 份与该 EIN 相关的原始文件记录。")
                # 打印最新一份记录的 Object ID
                latest_filing = data[0]
                print(f"最新一份文件的 Object ID 是: {latest_filing.get('object_id')}")
            else:
                print("找到了记录，但格式可能不是预期的列表。")

            print("---------------------------------\n")

        else:
            logging.error(f"❌ 失败！'efilexml' 端点返回错误状态码: {response.status_code}")
            logging.error(f"错误详情: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ 在请求 'efilexml' 端点时发生网络错误: {e}")
        return False

    # --- 任务 2: 验证 990basic120fields 端点 (获取解析好的关键数据) ---
    logging.info(f">>> 正在测试 '990basic120fields' 端点，查询 EIN: {TEST_EIN} 的解析后数据...")
    endpoint = "irs-data/990basic120fields"
    params = {'ein': TEST_EIN}

    try:
        response = requests.get(BASE_URL + endpoint, params=params, timeout=30)

        if response.status_code == 200:
            logging.info(f"✅ 成功！'990basic120fields' 端点返回状态码: {response.status_code}")
            data = response.json()

            print("\n--- '990basic120fields' 端点返回数据摘要 ---")
            if isinstance(data, list) and len(data) > 0:
                latest_data = data[0] # 通常返回的是一个列表，包含多年的数据
                print(f"成功获取到 EIN: {latest_data.get('ein')} 的解析后数据。")
                print(f"  组织名称: {latest_data.get('organization_name')}")
                print(f"  财年: {latest_data.get('tax_year')}")
                print(f"  总收入: ${latest_data.get('total_revenue')}")
            else:
                 print("找到了记录，但格式不是预期的列表或列表为空。")
            
            print("---------------------------------\n")
            return True # 最终成功

        else:
            logging.error(f"❌ 失败！'990basic120fields' 端点返回错误状态码: {response.status_code}")
            logging.error(f"错误详情: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ 在请求 '990basic120fields' 端点时发生网络错误: {e}")
        return False


if __name__ == "__main__":
    print("====== Giving Tuesday API 最终功能验证脚本 (V8) ======")
    success = final_verify_api()
    print("\n====== 验证完成 ======")
    if success:
        print("🏆🏆🏆 最终胜利！我们找到了正确的官方API，并成功获取了数据！")
        print("我们现在可以充满信心地进入下一阶段了。")
    else:
        print("ยังมีปัญหาอยู่ (Yāng mī pạỵh̄ā xyū̀ - 泰语“仍有问题”)。请检查上面的错误日志。")