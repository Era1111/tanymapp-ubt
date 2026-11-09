#!/usr/bin/env python3
"""Structural + independent numerical checks. Does not claim browser visual QA."""
import json,math,zipfile
from pathlib import Path
from collections import Counter
p=Path(__file__).with_name('course.json');course=json.loads(p.read_text());byid={q['id']:q for d in course['lessons'] for q in d['quiz']}
checks={
'U1.1-02':(8,'8'),'U1.1-04':(2**10,'1024'),'U1.1-06':(9*8,'72'),'U1.1-07':(len('AB CD'),'5 байт'),'U1.1-08':(2**2,'4'),'U1.1-10':(24*4,'96 бит'),'U1.1-11':(math.ceil(math.log2(16)),'4'),'U1.1-12':((40*8+40*16)//8,'120 байт'),'U1.1-13':(64*8//128,'4'),'U1.1-14':(90*8//6,'120 байт'),'U1.1-15':(300*math.ceil(math.log2(256))//8,'300 байт'),
'U1.2-01':(32//8,'4'),'U1.2-02':(3*1024,'3072'),'U1.2-03':(2048//1024,'2'),'U1.2-05':(10*8,'80 бит'),'U1.2-06':(1.5*1024,'1536'),'U1.2-07':(3*20*40,'2400 байт'),'U1.2-08':(128*64*8//8//1024,'8 Кбайт'),'U1.2-09':(400*8//800,'4 с'),'U1.2-10':(.25*1024,'256'),'U1.2-11':(2*1024//300,'6'),'U1.2-12':(20*32*64*16//8//1024,'80 Кбайт'),'U1.2-13':(2*1024*1024*8//262144,'64 с'),'U1.2-15':(1000000000//(256*1024*1024),'3'),
'U1.3-12':(4*1024//700,'5'),'U1.3-15':(300+400+350-1024,'26 Мбайт жетпейді'),
'U1.4-12':(500+2*1024+1024**2,'1051124'),'U1.4-13':(2*math.ceil(100/4096)*4096,'8192 байт'),'U1.4-15':(256*256*24//8//1024,'192 Кбайт'),
'U1.5-06':(100-70,'30 Мбайт'),'U1.5-07':((100-70)/100*100,'30%'),'U1.5-08':(200*.75,'150 Мбайт'),'U1.5-11':((80-50)/80*100,'37,5%'),'U1.5-12':(60/.6,'100 Мбайт'),'U1.5-13':((1-.8*.75)*100,'40%'),'U1.5-14':(50*.8+100*.5,'90 Мбайт'),'U1.5-15':(math.ceil(95/20),'5')}
for id,(numeric,expected) in checks.items():
 q=byid[id];assert q['options'][q['answer_index']]==expected,(id,expected)
 import re
 label=float(re.match(r'[0-9]+(?:[.,][0-9]+)?',expected)[0].replace(',','.'))
 assert math.isclose(numeric,label), (id,numeric,label)
for d in course['lessons']:
 assert Counter(q['level'] for q in d['quiz'])==Counter(A=5,B=5,C=5)
 assert len(d['quiz'])==15 and len(d['practice'])==3
 for q in d['quiz']:
  assert len(q['options'])==len(set(q['options']))==5
  assert len(q['option_explanations'])==5
  assert q['correct_answer']=='ABCDE'[q['answer_index']]
 folder=p.parent.parent/d['slug']
 for f in ['lesson.html','lesson.pptx','lesson.pdf','textbook.pdf','quiz.json','teacher_guide.pdf','sources.json','assets/diagram.svg']:assert (folder/f).is_file(),f
 with zipfile.ZipFile(folder/'lesson.pptx') as z:
  slides=[n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')];assert len(slides)==21
print(f'Passed: {len(byid)} questions, {len(checks)} independent numerical answers, 5 complete topic packages.')
