from rich import print
from prettytable import PrettyTable as Table
import errors as error
import defaults as default

from rich.pretty import pprint

global csv, filename
csv = ['','']
filename = ['[unloaded]']
cache = ['','']


def load(name):
	try:
		with open(f'{name}.csv','r') as file:
			filename[0] = f'{name}.csv'
			rows = file.read().split('\n')
			columnData = rows.pop(0).split(',')
			fileData = []
			for row in rows:
				fileData.append(row.split(','))
			for columnName in columnData:
				columnData[columnData.index(columnName)] = columnName.strip().replace(' ','_')
			csv[0] = columnData
			if fileData[-1] == ['']:
				fileData.pop()
			csv[1] = fileData
			print(f'Loaded file "{name}.csv"')
			print(f'Dataset has {len(columnData)} columns and {len(fileData)} rows.')
	except FileNotFoundError:
		error.fileNotFound(name)

def parse(queryString):
	# Query formatting 
	queryParams = queryString.strip().split()
	queryMethod = queryParams.pop(0)
	# Query Validation
	if queryMethod not in default.MethodsMap.keys():
		error.methodNotFound(queryMethod)
		return
	if len(queryParams) != default.MethodsMap[queryMethod]:
		error.missingParams()
		return
	
	#Query Processing
	# Load
	if queryMethod == 'load':
		load(queryParams[0])
	#In
	elif queryMethod == 'in':
		columns = queryParams[0].split(',')
		operation = queryParams[1]
		condition = queryParams[2]
		# Query Parameter Validation
		for column in columns:
			if column not in csv[0]:
				error.columnError()
				return
		if operation not in default.ValidInOperations:
			error.inOperation(operation)
		# Select * condition
		if condition == '*':
			 dataSet = []
			 for column in columns:
			 	index = csv[0].index(column)
			 	columnDataSet = []
			 	for row in csv[1]:
			 		columnDataSet.append(row[index])
			 	dataSet.append(columnDataSet)
			 queryResult = []
			 for i in range(len(dataSet[0])):
			 	row = []
			 	for column in dataSet:
			 		row.append(column[i])
			 	queryResult.append(row)
			 cache[0] = columns
			 cache[1] = queryResult
			 tableOut()
	#save
	if queryMethod == 'save':
		raw = cache[1]
		raw.insert(0,cache[0])
		try:
			file = open(queryParams[0]+'.csv','w')
			file.write('')
		except:
			pass
		file = open(queryParams[0]+'.csv','a')
		for line in raw:
			file.write(str(line).lstrip('[').rstrip(']').replace("'",'')+ '\n')
		print(f'Saved recent query output to file named "{queryParams[0]}.csv".')
		
	#show
	if queryMethod == 'show':
		if queryParams[0] == 'table':
			columns = str(csv[0]).lstrip('[').rstrip(']').replace("'",'').replace(' ','')
			parse(f'in {columns} select *')
		elif queryParams[0] == 'columns':
			print(f'Columns in loaded file "{filename}"')
			print(csv[0])

def tableOut():
	table = Table()
	table.field_names = cache[0]
	for row in cache[1]:
		table.add_row(row)
	print(table)

def fromScript(script):
	queries = script.split(';')
	for query in queries:
		parse(query.strip())

def client():
	while True:
		parse(input('\n'+filename[0]+'/>'))
		
client()