'''

Function addparam searches for the line that contains the expected parameter data in IparamTable.txt, then adds these data to dictionary param. 

'''

def addparam(param, IparamTableFile):
  fItable = open(IparamTableFile,'r')
  data_exist=0 # number of data lines that fits searching criterion
  fItable.readline() # skip title line
  for row in fItable:
    row = row.split('\t') # split data line
    row[-1] = row[-1][:-1] # strip off endline character
    row = [float(item) for item in row]
    # if the first three parameters fit with what we need, add the following parameters into param.
    if row[0]==param['fr'] and row[1]==param['tau'] and row[2]==param['posNa']:
      param['spthr'] = row[3]
      param['mean'] = row[4]
      param['std'] = row[5]
      data_exist += 1
      break
    else: continue
  fItable.close()
  if data_exist==0:
    print('Error: No line in IparamTable matches given parameters!')
  elif data_exist>1:
    print('More than one group of data fit, param is overwritten!')
  else:
    print('Parameters are written in param.')
    return param
  
