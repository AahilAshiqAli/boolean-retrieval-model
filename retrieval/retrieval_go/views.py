from django.shortcuts import render, HttpResponse
import nltk
import string
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from django.conf import settings
import os
import re

filename_dictionary = ['1.txt', '2.txt', '3.txt', '7.txt', '8.txt', '9.txt', '11.txt', '12.txt', '13.txt', '14.txt', '15.txt', '16.txt', '17.txt', '18.txt', '21.txt', '22.txt', '23.txt', '24.txt', '25.txt', '26.txt']
inverted_index = None
search_text = 'cancer and overview'
doc_num = None
# Create your views here.

#.......................................................................................................................


def remove_punctuations_and_numbers(text):
  
    text_no_punctuations = re.sub(r'[^\w\s]', '', text)

    text_no_punctuations_numbers = re.sub(r'\d', '', text_no_punctuations)

    return text_no_punctuations_numbers




#........................................................................................................................


def setup_index():
    global filename_dictionary
    global inverted_index
    inverted_index = {}
    index = {}
    for file_name in filename_dictionary:
        full_path = os.path.join(settings.BASE_DIR, 'data', file_name)
        with open(full_path, 'r',encoding='windows-1252') as file:
            word = file.read()
            text = remove_punctuations_and_numbers(word)
            words = word_tokenize(text)
            index[file_name] = words
            
    
    stop_words_file = 'Stopword-List.txt'
    full_path = os.path.join(settings.BASE_DIR, 'data', stop_words_file)
    with open(full_path) as file:
        file_content = file.read()
    stop_words = word_tokenize(file_content)
    for filename,tokens in index.items():
      filtered_tokens = [token.lower() for token in tokens if token.lower()]
      index[filename] = filtered_tokens
    
    for filename,tokens in index.items():
      for i in range(len(tokens)):
        token = tokens[i]
        if token not in inverted_index.keys():
          inverted_index[token] = [1,{filename : [i]}]
        else:
          dic = inverted_index[token]
          dic[0] = dic[0]+1
          if filename in dic[1].keys():
            dic[1][filename].append(i)
          else:
            dic[1][filename] = [i]   

    modified_index = {}
    for token,items in inverted_index.items():
      if token not in string.ascii_lowercase and token not in stop_words:
        modified_index[token] = items
        
    inverted_index = {}
    ps = PorterStemmer()

    for token, item in modified_index.items():
        stemmed_token = ps.stem(token)

        if stemmed_token not in inverted_index:
            inverted_index[stemmed_token] = item
        else:
            val = inverted_index[stemmed_token]

            # Update frequency
            val[0] += item[0]

            # Update file-wise occurrences
            for key, values in item[1].items():
                if key in val[1]:
                    val[1][key].extend(values)
                    val[1][key].sort()
                else:
                    val[1][key] = values

            inverted_index[stemmed_token] = val



#...........................................................................................................................................





def conjunction(p1,p2):
  if type(p1) is dict:
    p1_doc = [int(row.split('.')[0]) for row in list(p1.keys())]
  else:
    p1_doc = p1
  if type(p2) is dict:
    p2_doc = [int(row.split('.')[0]) for row in list(p2.keys())]
  else:
    p2_doc = p2
  p1_doc.sort()
  p2_doc.sort()

  intersection = []

  # iterations are m + n
  m = len(p1_doc)
  n = len(p2_doc)
  i = 0 # current index of p1_doc
  j = 0 # current index of p2_doc

  while True:
    if i < m and j < n:
      if p1_doc[i] == p2_doc[j]:
        intersection.append(p1_doc[i])
        i += 1
        j += 1
      elif p1_doc[i] < p2_doc[j]:
        i += 1
      else:
        j += 1
    else:
      break
  return intersection



#...........................................................................................................................................




def disjunction(p1,p2):
  if type(p1) is dict:
    p1_doc = [int(row.split('.')[0]) for row in list(p1.keys())]
  else:
    p1_doc = p1
  if type(p2) is dict:
    p2_doc = [int(row.split('.')[0]) for row in list(p2.keys())]
  else:
    p2_doc = p2
  p1_doc.sort()
  p2_doc.sort()

  disjunct = []

  # iterations are m + n
  m = len(p1_doc)
  n = len(p2_doc)
  i = 0 # current index of p1_doc
  j = 0 # current index of p2_doc

  while True:
    if i < m and j < n:
      if p1_doc[i] == p2_doc[j]:
        disjunct.append(p1_doc[i])
        i += 1
        j += 1
      elif p1_doc[i] < p2_doc[j]:
        disjunct.append(p1_doc[i])
        i += 1
      else:
        disjunct.append(p2_doc[j])
        j += 1
    else:
      break

  while i < m:
      disjunct.append(p1_doc[i])
      i += 1

  while j < n:
    disjunct.append(p2_doc[j])
    j += 1

  return disjunct



#...........................................................................................................................................



def positional(p1,p2,k):
  answer = []
  p1_doc = [(int(row[0].split('.')[0]),row[1]) for row in list(p1.items())]
  p2_doc = [(int(row[0].split('.')[0]),row[1]) for row in list(p2.items())]
  
  p1_doc.sort(key=lambda x: x[0])
  p2_doc.sort(key=lambda x: x[0])
  # iterations are m + n
  m = len(p1_doc)
  n = len(p2_doc)
  i = 0 # current index of p1_doc
  j = 0 # current index of p2_doc

  while True:
    if i < m and j < n:
      if p1_doc[i][0] == p2_doc[j][0]:
        pos1 = p1_doc[i][1]
        pos2 = p2_doc[j][1]
        
        in2 = 0 # index of position of pos2
        l = len(pos2)

        for position1 in pos1:
          while in2 < l and abs(pos2[in2] - position1) <= k:
            answer.append(p1_doc[i][0])
            in2 += 1     
        i += 1
        j += 1
      elif p1_doc[i][0] < p2_doc[j][0]:
        i += 1
      else:
        j += 1
    else:
      break

  answer = list(set(answer))
  return answer






#...........................................................................................................................................

def query_process(search_text):
  
  global inverted_index
  ps = PorterStemmer()
  
  operators = ['and','or','not']
  
  query_tokens = [row for row in list(search_text.lower().split(" "))]
  arrays = [(term,[int(row.split(".")[0]) for row in inverted_index[ps.stem(term)][1]]) for term in query_tokens if term not in operators]
 
  flag = False
  try:
    for i in range(len(query_tokens)):
      if query_tokens[i] == "not":
        flag = True
        continue
      if flag == True and any(query_tokens[i] == t[0] for t in arrays):
        for elem, row in enumerate(arrays):
          if row[0] == query_tokens[i]:
            index = elem
            break
        arrays[index] = (query_tokens[i],negation(inverted_index[ps.stem(query_tokens[i])][1]))
        
  except Exception as e:
    print(type(e))
      # now i have negation for those jin ke aage negation laga hua
      
  logical_operators = [operator for operator in query_tokens if operator in ['and','or']]
  result_set = arrays[0][1]

  for i,(term,value) in enumerate(arrays[1:]):
    
    if i-1 < len(logical_operators):
      if logical_operators[i-1] == "and":
        result_set = conjunction(result_set,value)
      elif logical_operators[i-1] == "or":
        result_set = disjunction(result_set,value)


  return result_set








#...........................................................................................................................................


#.............................................................................................................


def negation(p1):
    global filename_dictionary
    negate = []
    p1_doc = [row for row in list(p1.keys())]
    p1_doc.sort()
    print(p1_doc)
    for i in filename_dictionary:
        if i not in p1_doc:
            negate.append(i)

    print(negate)
    return [int(row.split(".")[0]) for row in negate]





#...........................................................................................................................................





def index(request):
    info = {'variable' : 'Sending a dictionary to index html from views.py. Calling the key within curly braces would print its value'}
    # is tarah se hum model se cheezein fetch kr ke yahan sent kar sakte hain
    if inverted_index is None:
        setup_index()
    return render(request,'index.html',info)




#...............................................................................................................................................




def about(request):
    # in form, key is the name attribute of input ana vlaue is what user wrote
    global search_text
    ps = PorterStemmer()
    if request.method == 'POST':
        search_text = request.POST.get('search_text', None)
    
    
  # if / in search text then go to proximity query else query process
    try:
      if '/' in search_text:
        index = search_text.index('/')
        k = int(search_text[index+1:index+2])
        q1 = ps.stem(search_text.split(' ')[0].lower())
        q2 = ps.stem(search_text.split(' ')[1].lower())
        query_result = positional(inverted_index[q1][1],inverted_index[q2][1],k)
      else:
        query_result = query_process(search_text)
    except:
      return render(request, 'question.html', {'error_message': 'No matching found for given word in inverted index OR error in positional query syntax make sure after / there should be no space like /3'})
    docs_list = [os.path.join(settings.BASE_DIR, 'data', str(row)+'.txt') for row in query_result]
    read = []
    length = len(query_result)
    for file_name in docs_list:
      full_path = os.path.join(settings.BASE_DIR, 'data', file_name)
      with open(full_path, 'r',encoding='windows-1252') as file:
        word = file.read()
        read.append(word[:300]) 
      
    qw = []   
    for i in range(length):
      q = {"res" : query_result[i], "name" : docs_list[i], "doc_info" : read[i]}
      qw.append(q)
   
            
    return render(request,'about.html',{'q' : qw, "frequency" : length})




#...............................................................................................................................................




def services(request):
  global doc_num
  try:
    if request.method == 'GET':
      doc_num = request.GET.get('document_number')
    print(doc_num)
    with open(doc_num) as file:
      detail = file.read()
  except:
    return render(request, 'question.html', {'error_message': 'Select document first from Search results. Previous page not saved'})
  return render(request,'services.html',{'d' : detail})

# django how to make admin users and generate default tables 55 mins.


