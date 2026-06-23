function transposeVerticalToHorizontal(data) {
  if (!data || data.length === 0) {
    return [[]];
  }
  
  // 使用map方法将纵向数组转换为横向数组
  const transposedData = [data.map(row => row[0])];
  return transposedData;
}

function getSourceSheetData(spreadsheetId, sheetName, range) {
  try {
    const spreadsheet = SpreadsheetApp.openById(spreadsheetId);
    const sheet = spreadsheet.getSheetByName(sheetName);
    const dataRange = sheet.getRange(range);
    const data = dataRange.getValues();
    return data;
  } catch (error) {
    Logger.log('Error getting source sheet data: ' + error.message);
    throw error;
  }
}

function createDestinationSpreadsheet(sourceSpreadsheetId, sheetName, destinationFolderId) {
  try {
    const sourceSpreadsheet = SpreadsheetApp.openById(sourceSpreadsheetId);
    const destinationFolder = DriveApp.getFolderById(destinationFolderId);
    
    // 创建副本
    const newSpreadsheet = DriveApp.getFileById(sourceSpreadsheetId).makeCopy(sheetName, destinationFolder);
    const newSpreadsheetId = newSpreadsheet.getId();
    
    return newSpreadsheetId;
  } catch (error) {
    Logger.log('Error creating destination spreadsheet: ' + error.message);
    throw error;
  }
}

function writeDataToDestination(spreadsheetId, startCell, data, sheetName) {
  try {
    const spreadsheet = SpreadsheetApp.openById(spreadsheetId);
    const sheet = spreadsheet.getSheetByName(sheetName);
    
    // 解析起始单元格坐标
    const range = sheet.getRange(startCell);
    const startRow = range.getRow();
    const startColumn = range.getColumn();
    
    // 写入转置后的数据
    if (data && data.length > 0) {
      const numColumns = data[0].length;
      const writeRange = sheet.getRange(startRow, startColumn, 1, numColumns);
      writeRange.setValues(data);
    }
    
    // 在B2单元格写入源Sheet名字
    sheet.getRange('B2').setValue(sheetName);
    
  } catch (error) {
    Logger.log('Error writing data to destination: ' + error.message);
    throw error;
  }
}

function processData(spreadsheetId, sheetName, range, startCell, destinationFolderId) {
  try {
    // 1. 读取源表数据
    const sourceData = getSourceSheetData(spreadsheetId, sheetName, range);
    
    // 2. 转置数据
    const transposedData = transposeVerticalToHorizontal(sourceData);
    
    // 3. 创建目标表副本
    const newSpreadsheetId = createDestinationSpreadsheet(spreadsheetId, sheetName, destinationFolderId);
    
    // 4. 写入数据到目标表
    writeDataToDestination(newSpreadsheetId, startCell, transposedData, sheetName);
    
    return {
      success: true,
      message: '数据处理完成',
      newSpreadsheetId: newSpreadsheetId
    };
  } catch (error) {
    return {
      success: false,
      message: error.message
    };
  }
}

function getSheets(spreadsheetId) {
  try {
    const spreadsheet = SpreadsheetApp.openById(spreadsheetId);
    const sheets = spreadsheet.getSheets();
    return sheets.map(sheet => sheet.getName());
  } catch (error) {
    Logger.log('Error getting sheets: ' + error.message);
    return [];
  }
}

function doGet() {
  return HtmlService.createHtmlOutputFromFile('index');
}
