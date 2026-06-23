# Google Sheets 数据转置工具

## 功能描述

该Python脚本用于从公开的Google Sheets链接读取数据，将纵向数据（列）转置为横向数据（行），并写入到本地Excel文件中。

## 依赖库

- pandas：用于读取Google Sheets数据
- openpyxl：用于操作Excel文件
- requests：用于网络请求
- tkinter：用于创建GUI界面

## 安装依赖

```bash
pip install pandas openpyxl requests
```

## 使用方法

1. **运行脚本**：
   ```bash
   python google_sheets_transpose.py
   ```

2. **输入参数**：
   - **Sheet 名称**：输入或选择要处理的Sheet名称（如 April 14）
   - **读取范围**：输入要读取的纵向数据范围（如 Q3:Q19）
   - **本地Excel文件**：点击"浏览"按钮选择本地现有的Excel文件
   - **目标起始单元格**：输入数据写入的起始单元格（如 B2）

3. **执行操作**：
   - 点击"执行转置操作"按钮
   - 脚本会从Google Sheets读取数据，转置后写入本地Excel文件
   - 在B2单元格写入Sheet名称
   - 询问是否根据Sheet名称重命名本地文件

## 技术实现

1. **数据读取**：
   - 使用pandas直接读取Google Sheets的CSV导出版本
   - 无需API Key，只需提供公开的Google Sheets链接

2. **数据转置**：
   - 将纵向数组（如 [[v1],[v2],[v3]]）转换为横向数组（如 [[v1, v2, v3]]）
   - 使用列表推导式和map函数实现

3. **本地写入**：
   - 使用openpyxl打开本地Excel文件
   - 从指定起始单元格开始横向写入转置后的数据
   - 在B2单元格写入Sheet名称

4. **用户界面**：
   - 使用tkinter创建直观的图形界面
   - 提供文件选择对话框
   - 显示操作结果和错误信息

## 注意事项

- 确保Google Sheets链接是公开的，否则无法读取数据
- 输入的范围格式必须正确（如 Q3:Q19）
- 目标Excel文件必须存在
- 脚本会覆盖目标文件中的现有数据，请谨慎操作
- 对于大型表格，读取和处理可能需要一些时间

## 示例

1. **读取范围**：Q3:Q19
2. **目标单元格**：B2
3. **执行结果**：
   - 从Google Sheets读取Q3:Q19的纵向数据
   - 转置为横向数据
   - 从B2开始横向写入数据（占据B2到R2）
   - 在B2单元格写入Sheet名称
   - 询问是否重命名文件
