import StringIO, locale
locale.setlocale(locale.LC_NUMERIC, "")

############################################
#confusion matrix printing
############################################
def __format_num(num):
    """Format a number according to given places.
    Adds commas, etc. Will truncate floats into ints!"""
    try:
      inum = int(num)
      return locale.format("%.*f", (0, inum), True)
    except (ValueError, TypeError):
      return str(num)

def __get_max_width(table, index):
    """Get the maximum width of the given column index"""
    return max([len(__format_num(row[index])) for row in table])

def printConfusionMatrix(mat, labels):
  assert mat.shape[0] == len(labels)
  labMat = [ ["   "]+labels ]
  for idx, row in enumerate(mat):
    r = [ labels[idx]+"_true" ] 
    for n in row:
      r.append(n)
    labMat.append(r)

  #get column paddings
  col_paddings = []
  for i in range(len(labMat[0])):
    col_paddings.append(__get_max_width(labMat, i))
  
  out = StringIO.StringIO()
  for row in labMat:
    # left col
    print >> out, row[0].ljust(col_paddings[0] + 1),
    # rest of the cols
    for i in range(1, len(row)):
      col = __format_num(row[i]).rjust(col_paddings[i] + 2)
      print >> out, col,
    print >> out 
  print out.getvalue()  


