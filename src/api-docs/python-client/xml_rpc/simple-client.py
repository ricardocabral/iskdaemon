# simple isk-daemon test program
from xmlrpclib import ServerProxy

server = ServerProxy("http://localhost:31128/RPC")
data_dir = "/media/media2/prj/net.imgseek.imgdb/src-tests/data/"

#server = ServerProxy("http://192.168.2.6:31128/RPC")
#data_dir = "/home/rnc/workspace/net.imgseek.imgdb/src-tests/data/"

print server

def start_test(tst):
    print '-'*8 + ' ' + tst

def full_run():
    
    start_test('create db')
    
    assert server.createDb(1) == True
    
    start_test('add imgs')
    
    assert server.addImg(1, 7,data_dir+"DSC00007.JPG") == 1
    assert server.addImg(1, 6,data_dir+"DSC00006.JPG") == 1
    assert server.addImg(1, 14,data_dir+"DSC00014.JPG") == 1
    assert server.addImg(1, 17,data_dir+"DSC00017.JPG") == 1
    
    start_test('img count')
    
    assert server.getDbImgCount(1) == 4
    
    start_test('image is on db')
    
    assert server.isImgOnDb(1,7) == True
    
    start_test('save db')
    
    assert server.saveAllDbs() == 1
    
    start_test('reset db')
    
    assert server.resetDb(1) == 1
    assert server.getDbImgCount(1) == 0
    
    start_test('load db')
    
    assert server.loadAllDbs() == 1
    
    assert server.getDbImgCount(1) == 4
    
    assert server.isImgOnDb(1,7) == 1
    assert server.isImgOnDb(1,733) == 0
    
    start_test('remove img')
    
    assert server.removeImg(1,7) == 1
    assert server.removeImg(1,73232) == 0
    assert server.getDbImgCount(1) == 3
    assert server.isImgOnDb(1,7) == 0
    assert server.getDbImgIdList(1) == [6,14,17]
            
    start_test('list database spaces')
    
    assert server.getDbList() == [1]
    
    start_test('add more random images')
    
    fnames = [data_dir+"DSC00007.JPG",
              data_dir+"DSC00006.JPG",
              data_dir+"DSC00014.JPG",
              data_dir+"DSC00017.JPG"
              ]
    
    import random
    for i in range(20,60):
        assert server.addImg(1, i, random.choice(fnames)) == 1
    
    start_test('add keywords')
    
    assert server.addKeywordImg(1,142,3) == False
    assert server.addKeywordImg(1,14,1) == True
    assert server.addKeywordImg(1,14,2) == True
    assert server.addKeywordImg(1,14,3) == True
    assert server.addKeywordImg(1,14,4) == True
    assert server.addKeywordImg(1,17,3) == True
    assert server.addKeywordImg(1,21,3) == True
    assert server.addKeywordImg(1,22,5) == True
    
    start_test('get keywords')
    
    assert server.getKeywordsImg(1,14) == [1,2,3,4]
    assert server.getKeywordsImg(1,17) == [3]
    assert server.getKeywordsImg(1,21) == [3]
    assert server.getKeywordsImg(1,20) == []
    
    start_test('remove keywords')
    
    assert server.removeAllKeywordImg(1,17) == True
    assert server.getKeywordsImg(1,17) == []
    
    start_test('save db')
    
    assert server.saveAllDbs() == 1
    
    start_test('reset db')
    
    assert server.resetDb(1) == 1
    assert server.getDbImgCount(1) == 0
    
    start_test('load db')
    
    assert server.loadAllDbs() == 1
    assert server.getDbImgCount(1) == 43
    
    start_test('get keywords')
    
    assert server.getKeywordsImg(1,14) == [1,2,3,4]

    start_test('query by a keyword')

    # 3: 14, 17, 21
    # 4: 14
    # 5: 22
    
    
    res = server.getAllImgsByKeywords(1, 30, 1, '3')
    assert 14 in res
    assert 17 in res
    assert 21 in res 

    res = server.getAllImgsByKeywords(1, 30, 0, '3,4')
    assert 14 in res
    assert 17 in res
    assert 21 in res
     
    res = server.getAllImgsByKeywords(1, 30, 0, '3,4,5')
    assert 14 in res
    assert 17 in res
    assert 21 in res 
    assert 22 in res 

    res = server.getAllImgsByKeywords(1, 30, 1, '5') 
    assert 22 in res
     
    res = server.getAllImgsByKeywords(1, 30, 1, '3,4') 
    assert 14 in res
    
    start_test('query similarity')
    
    assert len(server.queryImgID(1,6, 3)) == 4    

    start_test('query similarity by a keyword')
    
    #def queryImgIDKeywords(dbId, imgId, numres, kwJoinType, keywords):
    res = server.queryImgIDKeywords(1,6, 3,0,'3,4')
    resids = [r[0] for r in res]
    assert 17 in resids
   
   #  start_test('mostPopularKeywords')
   #  
   #  assert server.addKeywordImg(1,50,1) == True
   #  assert server.addKeywordImg(1,50,2) == True
   #  assert server.addKeywordImg(1,50,3) == True
   #  assert server.addKeywordImg(1,51,1) == True
   #  assert server.addKeywordImg(1,51,2) == True
   #  assert server.addKeywordImg(1,51,3) == True
   #  assert server.addKeywordImg(1,52,3) == True
   #  
   # # dbId, imgs, excludedKwds, count, mode    
   #  res = server.mostPopularKeywords(1, '50,51,52', '1', 3, 0)
   #  resmap = {}
   #  for i in range(len(res)/2):
   #      resmap[res[i*2]] = res[i*2+1]
   #  assert 1 not in resmap.keys()
   #  assert resmap[3] == 3
    
    start_test('full_run finished')

start_test('all tests STARTED')    
full_run()
start_test('all tests FINISHED')