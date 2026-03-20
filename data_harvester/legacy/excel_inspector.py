import pandas as pd
import os

# --- 配置区 ---
# 确保这个文件名和你 reference 文件夹里的 Excel 文件名完全一致
DICTIONARY_FILE_PATH = os.path.join('reference', 'GTDC 990 API - Data Dictionary.xlsx')

def inspect_excel_sheets(file_path: str):
    """
    读取一个 Excel 文件并打印出其中所有工作表（Sheet）的名字。
    """
    print(f"====== 正在检查 Excel 文件: {file_path} ======")
    try:
        if not os.path.exists(file_path):
            print(f"❌ 错误：文件未找到！请确认路径和文件名是否正确。")
            return

        # 使用 pd.ExcelFile() 来打开文件，这是一个更稳健的方式
        xls = pd.ExcelFile(file_path)
        
        # .sheet_names 属性会返回一个包含所有工作表名称的列表
        sheet_names = xls.sheet_names
        
        print("\n✅ 成功读取文件！以下是文件中包含的所有工作表 (Sheet) 名称：")
        print("----------------------------------------------------")
        for name in sheet_names:
            print(f"  -> {name}")
        print("----------------------------------------------------")
        
        print("\n下一步：请从上面的列表中，复制那个看起来最像'基础120字段'的工作表的全名，")
        print("然后粘贴到 data_harvester_v1.py 脚本的 'sheet_name' 参数里。")

    except Exception as e:
        print(f"\n❌ 读取 Excel 文件时发生错误: {e}")
        print("💡 请确认文件没有损坏，并且你已经安装了 openpyxl (`pip install openpyxl`)。")

if __name__ == "__main__":
    inspect_excel_sheets(DICTIONARY_FILE_PATH)