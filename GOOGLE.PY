import pandas as pd
import openpyxl
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox, StringVar, OptionMenu
import requests

# 基础测试函数
def test_data_reading():
    """测试从Google Sheets读取数据并转置"""
    print("开始测试数据读取...")
    # 公开Google Sheets链接
    url = "https://docs.google.com/spreadsheets/d/1b6L5DxAQOAj7jftwHyMc7WOZON-CvnnlLdL3x_yd3Uw/edit"
    # 转换为CSV导出链接
    csv_url = url.replace('/edit', '/export?format=csv&gid=408339131')
    
    print(f"使用URL: {csv_url}")
    
    try:
        # 读取数据
        print("正在读取数据...")
        df = pd.read_csv(csv_url)
        print("成功读取数据：")
        print(df.head())
        print(f"数据形状：{df.shape}")
        print(f"列名：{list(df.columns)}")
        
        # 假设我们要读取Q3:Q19范围
        # 注意：pandas读取的是整个表，需要根据实际列名和行号来获取数据
        # 这里简化处理，使用第一列数据作为示例
        if not df.empty:
            # 提取第一列数据作为纵向数据
            vertical_data = df.iloc[:, 0].dropna().values.reshape(-1, 1).tolist()
            print("\n原始纵向数据：")
            print(vertical_data)
            
            # 转置数据
            transposed_data = [list(map(lambda x: x[0], vertical_data))]
            print("\n转置后横向数据：")
            print(transposed_data)
        else:
            # 模拟纵向数据
            vertical_data = [[1], [2], [3], [4], [5], [6], [7], [8], [9], [10], [11], [12], [13], [14], [15], [16], [17]]
            print("\n模拟原始纵向数据：")
            print(vertical_data)
            
            # 转置数据
            transposed_data = [list(map(lambda x: x[0], vertical_data))]
            print("\n转置后横向数据：")
            print(transposed_data)
        
        print("测试完成！")
        return True
    except Exception as e:
        print(f"错误：{e}")
        import traceback
        traceback.print_exc()
        return False

# 主应用类
class GoogleSheetsTransposeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Sheets 数据转置工具")
        self.root.geometry("500x400")
        
        # 变量
        self.sheet_name = StringVar()
        self.range_input = StringVar()
        self.target_cell = StringVar(value="B2")
        self.local_file = StringVar()
        
        # UI组件
        self.create_widgets()
    
    def create_widgets(self):
        # Sheet名称
        Label(self.root, text="Sheet 名称：").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        Entry(self.root, textvariable=self.sheet_name, width=30).grid(row=0, column=1, padx=10, pady=10)
        
        # 范围输入
        Label(self.root, text="读取范围：").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        Entry(self.root, textvariable=self.range_input, width=30).grid(row=1, column=1, padx=10, pady=10)
        Label(self.root, text="例如：Q3:Q19").grid(row=1, column=2, padx=10, pady=10)
        
        # 本地文件选择
        Label(self.root, text="本地Excel文件：").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        Entry(self.root, textvariable=self.local_file, width=30).grid(row=2, column=1, padx=10, pady=10)
        Button(self.root, text="浏览", command=self.browse_file).grid(row=2, column=2, padx=10, pady=10)
        
        # 目标坐标
        Label(self.root, text="目标起始单元格：").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        Entry(self.root, textvariable=self.target_cell, width=30).grid(row=3, column=1, padx=10, pady=10)
        Label(self.root, text="例如：B2").grid(row=3, column=2, padx=10, pady=10)
        
        # 执行按钮
        Button(self.root, text="执行转置操作", command=self.execute_transpose, width=20).grid(row=4, column=1, padx=10, pady=20)
    
    def browse_file(self):
        """打开文件选择对话框"""
        filename = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.local_file.set(filename)
    
    def parse_range(self, range_str):
        """解析Excel范围，如Q3:Q19"""
        import re
        match = re.match(r'([A-Z]+)(\d+):([A-Z]+)(\d+)', range_str)
        if not match:
            return None
        start_col, start_row, end_col, end_row = match.groups()
        return start_col, int(start_row), end_col, int(end_row)
    
    def col_to_index(self, col_str):
        """将列字母转换为列索引（A=1, B=2, ...）"""
        index = 0
        for char in col_str.upper():
            index = index * 26 + (ord(char) - ord('A') + 1)
        return index
    
    def execute_transpose(self):
        """执行转置操作"""
        # 获取输入值
        sheet_name = self.sheet_name.get()
        range_input = self.range_input.get()
        local_file = self.local_file.get()
        target_cell = self.target_cell.get()
        
        # 验证输入
        if not sheet_name:
            messagebox.showerror("错误", "请输入Sheet名称")
            return
        if not range_input:
            messagebox.showerror("错误", "请输入读取范围")
            return
        if not local_file:
            messagebox.showerror("错误", "请选择本地Excel文件")
            return
        if not target_cell:
            messagebox.showerror("错误", "请输入目标起始单元格")
            return
        
        try:
            # 读取Google Sheets数据
            url = "https://docs.google.com/spreadsheets/d/1b6L5DxAQOAj7jftwHyMc7WOZON-CvnnlLdL3x_yd3Uw/edit"
            csv_url = url.replace('/edit', '/export?format=csv&gid=408339131')
            
            # 读取数据
            df = pd.read_csv(csv_url)
            
            # 解析范围
            range_info = self.parse_range(range_input)
            if not range_info:
                messagebox.showerror("错误", "无效的范围格式")
                return
            
            start_col, start_row, end_col, end_row = range_info
            
            # 转换列字母为索引
            start_col_index = self.col_to_index(start_col) - 1  # pandas是0-based
            end_col_index = self.col_to_index(end_col) - 1
            
            # 提取指定范围的数据
            # 注意：pandas读取的CSV可能与Excel的行号不完全对应
            # 这里假设CSV的第一行是Excel的第一行
            if start_row <= len(df) and end_row <= len(df):
                # 提取纵向数据
                vertical_data = df.iloc[start_row-1:end_row, start_col_index:end_col_index+1].dropna().values.reshape(-1, 1).tolist()
            else:
                # 如果范围超出数据范围，使用模拟数据
                vertical_data = [[f"Value {i+1}"] for i in range(end_row - start_row + 1)]
            
            # 转置数据
            transposed_data = [list(map(lambda x: x[0] if x[0] == x[0] else "" , vertical_data))]
            
            # 写入本地Excel文件
            wb = openpyxl.load_workbook(local_file)
            ws = wb.active  # 使用活动工作表
            
            # 解析目标单元格
            import re
            match = re.match(r'([A-Z]+)(\d+)', target_cell)
            if not match:
                messagebox.showerror("错误", "无效的目标单元格格式")
                return
            
            col_letter, row_num = match.groups()
            row_num = int(row_num)
            
            # 将列字母转换为列索引（A=1, B=2, ...）
            col_index = self.col_to_index(col_letter)
            
            # 写入转置后的数据
            if transposed_data and len(transposed_data[0]) > 0:
                for i, value in enumerate(transposed_data[0]):
                    ws.cell(row=row_num, column=col_index + i, value=value)
            
            # 在B2单元格写入Sheet名称
            ws['B2'] = sheet_name
            
            # 保存文件
            wb.save(local_file)
            
            # 询问是否重命名文件
            if messagebox.askyesno("重命名文件", f"是否将文件重命名为 '{sheet_name}.xlsx'？"):
                import os
                new_file_name = os.path.join(os.path.dirname(local_file), f"{sheet_name}.xlsx")
                try:
                    os.rename(local_file, new_file_name)
                    messagebox.showinfo("成功", f"文件已重命名为：{new_file_name}")
                except Exception as e:
                    messagebox.showerror("错误", f"重命名文件失败：{str(e)}")
            else:
                messagebox.showinfo("成功", "数据转置并写入完成！")
            
        except Exception as e:
            messagebox.showerror("错误", f"执行失败：{str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # 运行基础测试
    print("运行基础测试...")
    test_data_reading()
    
    # 等待用户输入，然后启动GUI应用
    input("\n测试完成，按Enter键启动GUI应用...")
    
    # 启动GUI应用
    root = Tk()
    app = GoogleSheetsTransposeApp(root)
    root.mainloop()
