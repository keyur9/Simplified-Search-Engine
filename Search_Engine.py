# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 19:07:51 2015

@author: Keyur Doshi
Project: Search Engine Implementation
Description : P-9.4 Implement the simplified search engine described in Section 9.2.4 for the page of a small Web site. 
              Use all the winds in the pages of the site as index terms excluding stop words such as articles, prepositions, and pronouns.
Files Included: INPUT FILE : doc1.txt and doc2.txt
                OUTPUT FILE: output.txt

"""

# In[0]:
"""
    Importing libraries 
"""

from collections import Counter
_WORD_MIN_LENGTH = 3
cnt = Counter()
from nltk.corpus import stopwords
cacheStopwords = stopwords.words('english')

def word_split(text):
    """
    Split a text in words. Returns a list of tuple that contains
    (word, location) location is the starting byte position of the word.
    """
    word_list = []
    wcurrent = []
    windex = None

    for i, c in enumerate(text):
        if c.isalnum():
            wcurrent.append(c)
            windex = i
        elif wcurrent:
            word = u''.join(wcurrent)
            word_list.append((windex - len(word) + 1, word))
            wcurrent = []

    if wcurrent:
        word = u''.join(wcurrent)
        word_list.append((windex - len(word) + 1, word))

    return word_list

def words_cleanup(words):
    """
    Remove words with length less then a minimum and stopwords.
    """
    cleaned_words = []
    for index, word in words:
        if len(word) < _WORD_MIN_LENGTH or word in cacheStopwords:
            continue
        cleaned_words.append((index, word))
    return cleaned_words
  
def words_normalize(words):
    """
    Do a normalization process on words. In this case is just a tolower(),
    but you can add accents stripping, convert to singular and so on...
    """
    normalized_words = []
    for index, word in words:
        wnormalized = word.lower()
        normalized_words.append((index, wnormalized))
    return normalized_words

def word_index(text):
    """
    Just a helper method to process a text.
    It calls word split, normalize and cleanup.
    """
    words = word_split(text)
    words = words_normalize(words)
    words = words_cleanup(words)
    return words


def inverted_index(text):
    """
    Create an Inverted-Index of the specified text document.
        {word:(cnt[num_words])}
    """
    inverted = {}
    num_words = 0
    for index, word in word_index(text):
        locations = inverted.setdefault(word, [])
        locations.append(cnt[num_words])

    return inverted

def inverted_index_add(inverted, doc_id, doc_index):
    """
    Add Invertd-Index doc_index of the document doc_id to the 
    Multi-Document Inverted-Index (inverted), 
    using doc_id as document identifier.
        {word:{doc_id:(cnt[num_words])}}
    """
    for word, locations in doc_index.iteritems():
        indices = inverted.setdefault(word, {})
        indices[doc_id] = locations
    return inverted

# In[1]:
"""
    Adding Searching and Removing methods for words in trie
"""

class patricia():
    def __init__(self):
        self._data = {}

    def addWord(self, word):
        data = self._data
        i = 0
        while 1:
            try:
                node = data[word[i:i+1]]
            except KeyError:
                if data:
                    data[word[i:i+1]] = [word[i+1:],{}]
                else:
                    if word[i:i+1] == '':
                        return
                    else:
                        if i != 0:
                            data[''] = ['',{}]
                        data[word[i:i+1]] = [word[i+1:],{}]
                return

            i += 1
            if word.startswith(node[0],i):
                if len(word[i:]) == len(node[0]):
                    if node[1]:
                        try:
                            node[1]['']
                        except KeyError:
                            data = node[1]
                            data[''] = ['',{}]
                    return
                else:
                    i += len(node[0])
                    data = node[1]
            else:
                ii = i
                j = 0
                while ii != len(word) and j != len(node[0]) and \
                      word[ii:ii+1] == node[0][j:j+1]:
                    ii += 1
                    j += 1
                tmpdata = {}
                tmpdata[node[0][j:j+1]] = [node[0][j+1:],node[1]]
                tmpdata[word[ii:ii+1]] = [word[ii+1:],{}]
                data[word[i-1:i]] = [node[0][:j],tmpdata]
                return

    def isWord(self,word):
        data = self._data
        i = 0
        while 1:
            try:
                node = data[word[i:i+1]]
            except KeyError:
                return False
            i += 1
            if word.startswith(node[0],i):
                if len(word[i:]) == len(node[0]):
                    if node[1]:
                        try:
                            node[1]['']
                        except KeyError:
                            return False
                    return True
                else:
                    i += len(node[0])
                    data = node[1]
            else:
                return False

    def isPrefix(self,word):
        data = self._data
        i = 0
        wordlen = len(word)
        while 1:
            try:
                node = data[word[i:i+1]]
            except KeyError:
                return False
            i += 1
            if word.startswith(node[0][:wordlen-i],i):
                if wordlen - i > len(node[0]):
                    i += len(node[0])
                    data = node[1]
                else:
                    return True
            else:
                return False

    def removeWord(self,word):
        data = self._data
        i = 0
        while 1:
            try:
                node = data[word[i:i+1]]
            except KeyError:
                print "Word is not in trie."
                return
            i += 1
            if word.startswith(node[0],i):
                if len(word[i:]) == len(node[0]):
                    if node[1]:
                        try:
                            node[1]['']
                            node[1].pop('')
                        except KeyError:
                            print "Word is not in trie."
                        return
                    data.pop(word[i-1:i])
                    return
                else:
                    i += len(node[0])
                    data = node[1]
            else:
                print "Word is not in trie."
                return


    __getitem__ = isWord


# In[5]:

""" 
 Reading first document
"""

fileReader=open('doc1.txt')

for line in fileReader:
    doc1 = line
fileReader.close()

""" 
 Reading second document
"""

fileReader=open('doc2.txt')

for line in fileReader:
    doc2 = line
fileReader.close()
   
""" 
 Build Inverted-Index for documents
"""
inverted = {}
X = patricia()
documents = {'doc1':doc1, 'doc2':doc2}
for doc_id, text in documents.iteritems():
    doc_index = inverted_index(text)
    inverted_index_add(inverted, doc_id, doc_index)

""" 
 Adding Words in dictionary
"""
for word, count in inverted.items():
    print 'Words in dictionary:', word
    if word not in cacheStopwords:
        X.addWord(word)
""" 
 Printing Compressed Trie
"""
print X._data

# In[]:

"""
    Testing wether the word is in trie or not
    Provide the parameter (trie,word) and call in_trie function
    
"""
_end = '_end_'
def in_trie(trie, word):
    current_dict = trie
    for letter in word:
        if letter in current_dict:
            current_dict = current_dict[letter]
        else:
            return False
    else:
        if _end in current_dict:
            return True
        else:
            return False

# In[]:

""" 
 Writing into output file
"""
resultwriter=open('output.txt','w')
resultwriter.write(str(X._data))
resultwriter.close()

