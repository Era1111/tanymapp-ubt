#!/usr/bin/env python3
"""Build a course from authored JSON. Python 3.11+, reportlab, Pillow; Node + @oai/artifact-tool for PPTX."""
import argparse,json,html,os,subprocess,sys,shutil
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether,Flowable
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
FONTDIR=Path(os.getenv('COURSE_FONT_DIR','/System/Library/Fonts/Supplemental'))
for name,file in [('TNR','Times New Roman.ttf'),('TNR-Bold','Times New Roman Bold.ttf'),('TNR-Italic','Times New Roman Italic.ttf')]:
 if not (FONTDIR/file).exists(): raise SystemExit(f'Missing font: {FONTDIR/file}. Set COURSE_FONT_DIR to licensed Times New Roman fonts.')
 pdfmetrics.registerFont(TTFont(name,str(FONTDIR/file)))
pdfmetrics.registerFontFamily('TNR',normal='TNR',bold='TNR-Bold',italic='TNR-Italic',boldItalic='TNR-Bold')
styles={
'p':ParagraphStyle('p',fontName='TNR',fontSize=11.5,leading=15.5,spaceAfter=8),
'h1':ParagraphStyle('h1',fontName='TNR-Bold',fontSize=23,leading=27,spaceAfter=16),
'h2':ParagraphStyle('h2',fontName='TNR-Bold',fontSize=16,leading=20,spaceBefore=9,spaceAfter=9),
'h3':ParagraphStyle('h3',fontName='TNR-Bold',fontSize=12.5,leading=16,spaceBefore=5,spaceAfter=6),
'small':ParagraphStyle('small',fontName='TNR',fontSize=9,leading=12,spaceAfter=5)}
def P(t,sty='p'):return Paragraph(escape(str(t)),styles[sty])
def paras(xs):return [P(x) for x in xs]
def page(canvas,doc):
 canvas.setFont('TNR',9);canvas.drawString(44,25,'ҰБТ информатика • I бөлім');canvas.drawRightString(551,25,str(doc.page))
def pdf(path,story):SimpleDocTemplate(str(path),pagesize=(595.28,841.89),rightMargin=44,leftMargin=44,topMargin=40,bottomMargin=43,title=path.stem,author='Авторлық оқу материалы').build(story,onFirstPage=page,onLaterPages=page)
def table(rows):
 n=len(rows[0]); t=Table([[P(c,'small') for c in r] for r in rows],colWidths=[507/n]*n,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'TNR'),('GRID',(0,0),(-1,-1),.5,colors.black),('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eeeeee')),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),5)]));return t
class Diagram(Flowable):
 def __init__(self,labels):Flowable.__init__(self);self.labels=labels;self.width=507;self.height=120
 def draw(self):
  c=self.canv;c.setFont('TNR',11)
  for i,label in enumerate(self.labels):
   x=i*128;c.rect(x,43,119,43);words=label.split();lines=[];line=''
   for w in words:
    if pdfmetrics.stringWidth(line+' '+w,'TNR',11)>108:lines.append(line);line=w
    else:line=(line+' '+w).strip()
   lines.append(line)
   for j,l in enumerate(lines):c.drawCentredString(x+59.5,69-j*13,l)
   if i<3:c.line(x+119,64,x+127,64)
  c.setFont('TNR',9);c.drawString(0,18,'Авторлық сызба. Байланыс пен реттіліктің оқу моделі.')
SPEC='https://new.testcenter.kz/wp-content/uploads/2025/10/28_Информатика_каз.pdf'
FORMAT='Бұл 15 сұрақ бір дұрыс жауапты авторлық жаттығулар. Әр сұрақта бес нұсқа бар. A/B/C бойынша 5/5/5 үлесі оқу үшін таңдалды. Ресми ҰБТ нұсқасының толық көшірмесі емес: 2026 спецификациясында 25 жеке бір жауапты, контекстегі 5 бір жауапты, 5 бір немесе бірнеше жауапты және 5 сәйкестендіру тапсырмасы бар. Ресми күрделілік үлесі 50/30/20, бұл жинақта 5/5/5.'
CONVENTION='Есеп шарты өзгеше болмаса: 1 Кбайт = 1024 байт, 1 Мбайт = 1024 Кбайт, 1 Гбайт = 1024 Мбайт; 1 байт = 8 бит. Мәтін мен растр есептерінде кодтау және қызметтік деректер туралы шартты оқыңыз.'
EXTRA=[dict(id='E1',title='NIST: Binary prefixes',url='https://physics.nist.gov/cuu/Units/binary.html',use='Екілік және ондық еселіктерді ажырату'),dict(id='E2',title='Unicode FAQ: UTF-8, UTF-16, UTF-32',url='https://www.unicode.org/faq/utf_bom.html',use='Бір таңба әрдайым бір байт емес'),dict(id='E3',title='ҰТО: 2026 информатика спецификациясы',url=SPEC,use='Ресми тапсырма түрлері мен күрделілік үлесі')]
def sources(d,books):
 return dict(topic_code=d['code'],page_numbering='PDF page index is one-based; cited printed page numbers match PDF pages in the relevant sections.',books=[dict(id=k,**books[k],used_pages=v,page_numbering='PDF және баспа беттері сәйкес',material_type='Теорияны тексеру және өз сөзімізбен жинақтау',copyright_status='Үшінші тараптың авторлық құқығы сақталады. Коммерциялық қайта басуға рұқсат берілмеген. Мәтін/сурет көшірілмеді.') for k,v in d['references'].items()],claims=[dict(claim=s['title'],source=s['source']) for s in d['sections']],external_sources=EXTRA,original_materials=[dict(material_type=t,origin='Осы жобаға жаңадан құрастырылған',copyright_status='Оқулықтан көшірілмеген; үшінші тарап суреттері мен логотиптері қолданылмаған') for t in ['Түсіндірмелер мен мысалдар','75 сұрақтың осы тақырыптағы 15 сұрағы','Векторлық сызба','HTML интерфейсі','Презентация макеті']],editorial_notes=['Оқулықтардағы 1 таңба = 1 байт мысалдары шартты модель ретінде берілді.','Ескі аппарат көлемдері қазіргі талап ретінде алынбады.','Архив міндетті түрде кішіреймейді; қызметтік дерек пен алдын ала сығу ескерілді.'])
def source_paras(d,books):
 out=[]
 for k,ps in d['references'].items():
  b=books[k];out.append(P(f"{k}. {b['authors']}. {b['title']}. {b['publisher']}, {b['year']}. {b['file']}, беттер: {', '.join(map(str,ps))}.",'small'))
 return out

def textbook(d,folder,books):
 s=[P(d['code'],'small'),P(d['title'],'h1'),P('Цифрлық оқулық • Өздігінен оқу','h2'),P('Оқу мақсаттары','h2')]+paras(d['goals'])+[P('Алдын ала білу қажет','h2'),P('; '.join(d['prerequisites'])),P('Жұмыс тәртібі','h2'),P('Теорияны оқыңыз. Сызба мен мысалды салыстырыңыз. Тапсырмаларды жауапқа қарамай орындаңыз. Содан кейін түсіндірмемен тексеріп, қатені түзетіңіз.'),P(CONVENTION),PageBreak(),P('Негізгі теория','h1')]
 for sec in d['sections']:s += [P(sec['title'],'h2'),P(sec['text']),P('Дереккөз: '+sec['source'],'small')]
 s += [PageBreak(),P('Терминдер, сызба және салыстыру','h1'),table(d['table']),Spacer(1,10),Diagram(d['diagram']),P('Сызбаны түсіндіру','h2'),P(d['diagram_caption']),P('Терминдер','h2')]
 for term,definition in d['cards']:s += [P(term,'h3'),P(definition)]
 s += [PageBreak(),P('Қадамдық мысалдар','h1')]
 for i,ex in enumerate(d['examples']):s += [P(f"{i+1}. {ex['question']}",'h2')]+paras([f'{j+1}) {v}' for j,v in enumerate(ex['steps'])])
 s += [P('Жиі кездесетін қателер','h2')]+paras(d['errors'])
 s += [PageBreak(),P('A, B, C деңгейіндегі практика','h1')]
 for x in d['practice']:s += [P(x['level']+' деңгейі','h2'),P(x['question']),P('Тексеру: '+x['answer'])]
 s += [P('Өзін-өзі тексеруге дайындық','h2'),P('Келесі беттердегі 15 сұраққа алдымен өзіңіз жауап беріңіз. Жауап кілті мен әр нұсқаның түсіндірмесі тесттен кейін беріледі.'),P(FORMAT,'small')]
 for level in 'ABC':
  s += [PageBreak(),P('Өзін-өзі тексеру: '+level+' деңгейі','h1'),P(CONVENTION,'small')]
  for qu in [x for x in d['quiz'] if x['level']==level]:
   s += [KeepTogether([P(qu['id']+'  '+qu['question'],'h3')]+[P('   /   '.join(f"{'ABCDE'[i]}) {v}" for i,v in enumerate(qu['options'])))])]
 for start in range(0,15,3):
  s += [PageBreak(),P('Жауаптар және түсіндірмелер','h1')]
  for qu in d['quiz'][start:start+3]:
   s += [P(f"{qu['id']} • Дұрыс жауап: {qu['correct_answer']}",'h3'),P(qu['explanation'])]
   for j,v in enumerate(qu['options']):
    if j!=qu['answer_index']:s += [P(f"{'ABCDE'[j]}) {v}: {qu['option_explanations'][j]}",'small')]
   s += [P('Тексерілетін дағды: '+qu['skill'],'small')]
 s += [PageBreak(),P('Қорытынды және қайталау','h1')]+paras(d['summary'])+[P('Қайталау карточкалары','h2')]
 for x,y in d['cards']:s += [P(x,'h3'),P(y)]
 s += [P('Келесі қадам','h2'),P('12–15 дұрыс жауап: аралас есептерге өтіңіз. 8–11: қате шыққан ұғымдар мен мысалдарды қайталаңыз. 0–7: теориядан бастап, мұғаліммен қателерді талдаңыз. Бұл оқу ұсынысы, ресми баға шкаласы емес.'),PageBreak(),P('Дереккөздер және шығу тегі','h1')]+source_paras(d,books)
 s += [P('Нақтылау үшін сыртқы дереккөздер','h2')]
 for x in EXTRA:s += [P(x['title']+' — '+x['use'],'small'),P(x['url'],'small')]
 s += [P('Оқулықтар фактілерді тексеру үшін пайдаланылды. Оқулық суреттері, кестелері және тапсырмалары көшірілген жоқ. Түсіндірмелер, мысалдар, тесттер және сызба жаңадан жасалды. Дереккөзге сілтеме оның суретін коммерциялық қайта жариялауға рұқсат бермейді. Толық тіркеу: sources.json.','small')]
 pdf(folder/'textbook.pdf',s)

def teacher(d,folder,books):
 s=[P(d['title'],'h1'),P('Мұғалімге нұсқаулық • 60 минут','h2'),P('Нәтиже','h2')]+paras(d['goals'])+[table([['Минут','Әрекет','Бақылау'],['0–5','Алдын ала білімді тексеру','Екі терминді түсіндіру'],['5–18','Теория және сызба','Оқушы байланыстарды өзі айтады'],['18–30','Үш қадамдық мысал','Әр қадамның себебін түсіндіреді'],['30–42','A/B/C практикалық жұмыс','Бірліктер мен болжамдарды жазады'],['42–55','Тесттен іріктелген тапсырмалар','Алдымен жеке жауап, кейін талдау'],['55–60','Қате талдау және қорытынды','Қайталау жоспары']]),P('Сабақты жүргізу','h2'),P('Презентацияда әр тапсырмадан кейінгі слайдта жауап бар. Жауапты оқушы өз шешімін түсіндіргеннен кейін ашыңыз. 15 тесттің бәрі 60 минутқа сыймаса, қалғанын өздік жұмысқа беріңіз. Бір сабақ бір тақырыпқа арналған, бөлімнің бес сабағы жалпы 300 минут.'),P('Диагностика','h2'),P(d['cards'][0][0]+' '+d['cards'][1][0]),PageBreak(),P('Жауап кілті және қате талдау','h1')]
 s += [table([['ID','Жауап','Деңгей','Дағды']]+[[x['id'],x['correct_answer'],x['level'],x['skill']] for x in d['quiz']])]
 s += [P('Түсіндіру кезінде назар аудару','h2')]+paras(d['errors'])+[P('Толық шешімдер','h2'),P('textbook.pdf ішіндегі «Жауаптар және түсіндірмелер» бөлімінде әр дұрыс жауап пен төрт қате нұсқа талданған. lesson.html жауаптан кейін сол түсіндірмелерді көрсетеді.'),PageBreak(),P('Бағалау және келесі сабақ','h1'),P('Әр сұрақ: 1 балл. Ең көбі: 15 балл. A, B, C деңгейлерін бөлек талдаңыз. Ұсынылатын меңгеру межесі: кемінде 12/15 және қате жауаптың себебін түсіндіре алу.'),P(FORMAT),P('Ресми дереккөз: '+SPEC,'small'),P('Үй жұмысы','h2'),P('Қате шыққан үш сұрақты қайта шешу. Әрқайсысы үшін дұрыс ережені, қате әрекетті және жаңа ұқсас мысалды жазу. Қайталау карточкаларын келесі күні қайта қарау.'),P('Онлайн режим','h2'),P('Прогресс пен жауаптар осы браузердің localStorage қоймасында сақталады, егер браузер рұқсат етсе. Серверлік сақтау қосылмаған. Тексерілген сұрақтарда алғашқы жауап есепке алынады. Қайта бастау батырмасы осы сабақтың жергілікті нәтижесін өшіреді.'),P('Дереккөздер','h2')]+source_paras(d,books)
 pdf(folder/'teacher_guide.pdf',s)

CSS='''*{box-sizing:border-box}html{scroll-behavior:smooth}body{font-family:"Times New Roman",Times,serif;background:#fff;color:#000;font-size:20px;line-height:1.55;margin:0}main{max-width:920px;margin:auto;padding:32px 24px 80px}h1{font-size:2.3rem;line-height:1.12}h2{font-size:1.65rem;line-height:1.2;margin:0 0 20px}h3{font-size:1.25rem;line-height:1.3}p{margin:12px 0}a{color:#000;text-underline-offset:3px}nav{border-block:1px solid;padding:18px 0;display:flex;flex-wrap:wrap;gap:10px 24px}section{padding:36px 0;border-bottom:1px solid #aaa;scroll-margin-top:75px}.meta,.source,small{font-size:15px}.top{position:sticky;top:0;background:white;border-bottom:1px solid;z-index:3;padding:8px 20px;display:flex;gap:18px;align-items:center;justify-content:center;font-size:16px}progress{max-width:200px;width:30%;accent-color:#000}button{font:inherit;color:#000;background:#fff;border:1px solid;padding:8px 16px;cursor:pointer}button:hover,button:focus{background:#eee}button:disabled{cursor:default;color:#555}input{accent-color:#000}label{display:block;margin:8px 0;padding:6px}fieldset{border:1px solid #777;margin:24px 0;padding:22px;min-width:0}legend{font-weight:bold;padding:0 8px}details{border-bottom:1px solid #bbb;padding:16px 0}summary{cursor:pointer}table{border-collapse:collapse;width:100%;font-size:17px}td,th{border:1px solid;padding:10px;text-align:left;vertical-align:top}.scroll{overflow:auto}img{max-width:100%;height:auto}.feedback{margin-top:18px;border-left:3px solid;padding-left:18px}.correct{font-weight:bold}.cards{display:grid;grid-template-columns:1fr 1fr;gap:0 24px}.check{font-size:16px;margin-top:24px}.error{font-weight:bold}pre{white-space:pre-wrap;overflow-wrap:anywhere;border:1px solid;padding:16px;font-size:16px}code{font-family:"Times New Roman",serif}.practice{margin:20px 0}footer{font-size:15px;padding-top:30px}.result{font-size:24px;font-weight:bold}@media(max-width:600px){body{font-size:18px}main{padding:24px 16px 60px}h1{font-size:2rem}.cards{display:block}fieldset{padding:15px 10px}td,th{padding:7px}nav{gap:8px 18px}.top{gap:10px;padding:8px}.source{overflow-wrap:anywhere}}@media print{.top,button,.check{display:none}section{break-inside:auto}details>*{display:block}}'''
CSS += Path(__file__).with_name('site-theme.css').read_text()
JS=r'''const DATA=JSON.parse(document.getElementById('lesson-data').textContent);const KEY='ubt-v1-'+DATA.code;let state={read:[],answers:{}};let storageOK=true;try{const old=JSON.parse(localStorage.getItem(KEY));if(old&&Array.isArray(old.read)&&old.answers&&typeof old.answers==='object')state=old;}catch(e){storageOK=false;}const text=(tag,s)=>{let e=document.createElement(tag);e.textContent=s;return e};function save(){try{localStorage.setItem(KEY,JSON.stringify(state));}catch(e){storageOK=false;}update();}function update(){let count=Object.keys(state.answers).filter(id=>DATA.quiz.some(q=>q.id===id)).length;let correct=DATA.quiz.filter(q=>state.answers[q.id]===q.answer_index).length;let done=document.querySelectorAll('.read:checked').length;let total=document.querySelectorAll('.read').length+DATA.quiz.length;let p=Math.round(100*(done+count)/total);document.getElementById('progress').value=p;document.getElementById('progress-label').textContent=p+'%';document.getElementById('score').textContent='Нәтиже: '+correct+' / '+DATA.quiz.length+'. Жауап берілді: '+count+'.';document.getElementById('storage').textContent=storageOK?'Нәтиже тек осы браузерде сақталады. Серверге жіберілмейді.':'Браузерде сақтау қолжетімсіз. Нәтиже осы бет жабылғанша ғана сақталады.';}
function showFeedback(q,root,selected){root.replaceChildren();root.append(text('p',(selected===q.answer_index?'Дұрыс. ':'Қате. ')+'Дұрыс жауап: '+'ABCDE'[q.answer_index]+'. '+q.explanation));let details=document.createElement('details');details.append(text('summary','Барлық нұсқаның түсіндірмесі'));q.options.forEach((opt,i)=>details.append(text('p','ABCDE'[i]+') '+opt+' — '+q.option_explanations[i])));root.append(details);root.append(text('small','Дағды: '+q.skill));}
const quiz=document.getElementById('quiz');DATA.quiz.forEach((q,index)=>{let fs=document.createElement('fieldset');fs.append(text('legend',(index+1)+'. '+q.level+' деңгейі'));fs.append(text('p',q.question));q.options.forEach((opt,i)=>{let label=document.createElement('label');let input=document.createElement('input');input.type='radio';input.name=q.id;input.value=i;label.append(input,document.createTextNode(' '+'ABCDE'[i]+') '+opt));fs.append(label)});let b=text('button','Жауапты тексеру');b.type='button';let result=document.createElement('div');result.className='feedback';result.setAttribute('aria-live','polite');function lock(selected){fs.querySelectorAll('input').forEach(x=>{x.checked=Number(x.value)===selected;x.disabled=true});b.disabled=true;showFeedback(q,result,selected)}b.onclick=()=>{let selected=fs.querySelector('input:checked');if(!selected){result.replaceChildren(text('p','Алдымен бір жауапты таңдаңыз.'));return}state.answers[q.id]=Number(selected.value);lock(Number(selected.value));save()};fs.append(b,result);quiz.append(fs);if(Number.isInteger(state.answers[q.id])&&state.answers[q.id]>=0&&state.answers[q.id]<5)lock(state.answers[q.id]);});document.querySelectorAll('.read').forEach(x=>{x.checked=state.read.includes(x.id);x.onchange=()=>{state.read=[...document.querySelectorAll('.read:checked')].map(z=>z.id);save();}});document.getElementById('reset').onclick=()=>{if(confirm('Осы сабақтың жауаптары мен прогресін өшіріп, қайта бастау керек пе?')){try{localStorage.removeItem(KEY);}catch(e){}location.reload();}};document.querySelectorAll('[data-copy]').forEach(b=>b.onclick=async()=>{const content=document.getElementById(b.dataset.copy).textContent;try{await navigator.clipboard.writeText(content);b.textContent='Көшірілді';}catch(e){const range=document.createRange();range.selectNodeContents(document.getElementById(b.dataset.copy));const sel=getSelection();sel.removeAllRanges();sel.addRange(range);b.textContent='Мәтін белгіленді: көшіріңіз';}});document.getElementById('export-result').onclick=()=>{const payload={schema_version:'1.0',topic_code:DATA.code,answers:state.answers,completed_at:new Date().toISOString(),score:DATA.quiz.filter(q=>state.answers[q.id]===q.answer_index).length,total:DATA.quiz.length};const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}));a.download=DATA.code+'-result.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);};update();'''
def svg(labels):
 rows=[]
 for i,label in enumerate(labels):
  y=15+i*90; rows.append(f'<rect x="80" y="{y}" width="640" height="62" fill="white" stroke="black"/><text x="400" y="{y+39}" text-anchor="middle" font-size="25" font-family="Times New Roman,serif">{html.escape(label)}</text>')
  if i<3:rows.append(f'<path d="M400 {y+62}V{y+88}m-5 -6l5 6 5 -6" fill="none" stroke="black"/>')
 return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 370" role="img" aria-label="Авторлық оқу сызбасы">'+''.join(rows)+'</svg>'
def html_lesson(d,folder,books):
 esc=html.escape
 chunks=[]
 def sec(id,title,body):chunks.append(f'<section id="{id}"><h2>{title}</h2>{body}<label class="check"><input class="read" id="read-{id}" type="checkbox"> Бұл бөлімді оқып түсіндім</label></section>')
 def ps(xs):return ''.join('<p>'+esc(v)+'</p>' for v in xs)
 sec('goals','1. Оқу мақсаттары',ps(d['goals']))
 sec('prereq','2. Алдын ала білу қажет',ps(d['prerequisites'])+f'<p class="meta">{esc(CONVENTION)}</p>')
 sec('theory','3. Негізгі теория',''.join(f'<h3>{esc(x["title"])}</h3><p>{esc(x["text"])}</p><p class="source">Дереккөз: {esc(x["source"])}</p>' for x in d['sections']))
 sec('terms','4. Терминдер',''.join(f'<h3>{esc(x)}</h3><p>{esc(y)}</p>' for x,y in d['cards']))
 sec('diagram','5. Сызба',f'<img src="assets/diagram.svg" alt="{esc(d["diagram_caption"])}"><p>{esc(d["diagram_caption"])}</p><small>Осы сабаққа жаңадан жасалған сызба.</small>')
 sec('examples','6. Қадамдық мысалдар',''.join(f'<h3>{esc(x["question"])}</h3><ol>'+''.join('<li>'+esc(v)+'</li>' for v in x['steps'])+'</ol>' for x in d['examples']))
 chunks[-1]=chunks[-1].replace('</section>', '<h3>Жазылым үлгісі</h3><pre><code id="copy-example">'+esc(d.get('copy_example',''))+'</code></pre><button type="button" data-copy="copy-example">Көшіру</button></section>')
 sec('comparison','7. Салыстыру кестесі','<div class="scroll"><table>'+''.join('<tr>'+''.join(f'<{"th" if i==0 else "td"}>{esc(v)}</{"th" if i==0 else "td"}>' for v in row)+'</tr>' for i,row in enumerate(d['table']))+'</table></div>')
 sec('mistakes','8. Жиі кездесетін қателер',ps(d['errors']))
 sec('practice','9. A, B, C деңгейіндегі тапсырмалар',''.join(f'<div class="practice"><h3>{x["level"]} деңгейі</h3><p>{esc(x["question"])}</p><details><summary>Шешімін тексеру</summary><p>{esc(x["answer"])}</p></details></div>' for x in d['practice']))
 sec('selftest','10. Өзін-өзі тексеру',f'<p>{esc(FORMAT)}</p><p>Алғашқы жауап есепке алынады. Барлық нұсқаның түсіндірмесі тексергеннен кейін ашылады.</p><div id="quiz"></div><p id="score" class="result" aria-live="polite"></p><p id="storage" class="meta"></p><button id="export-result">Нәтижені JSON түрінде жүктеу</button> <button id="reset">Қайта бастау</button>')
 sec('answers','11. Жауаптарды талдау','<p>Әр тест жауабынан кейін дұрыс жауаптың шешімі көрсетіледі. «Барлық нұсқаның түсіндірмесі» арқылы төрт қате нұсқаның себебін қараңыз. Толық жауап кілті баспа оқулықта да бар.</p><p>12–15: аралас тапсырмаларға өтіңіз. 8–11: қате тақырыптарды қайталаңыз. 0–7: теория мен мысалдарға оралыңыз. Бұл оқу бағдары, ресми баға емес.</p>')
 sec('summary','12. Қысқаша қорытынды',ps(d['summary']))
 sec('cards','13. Қайталау карточкалары','<div class="cards">'+''.join(f'<details><summary>{esc(x)}</summary><p>{esc(y)}</p></details>' for x,y in d['cards'])+'</div>')
 src=''.join(f'<p>{k}. {esc(books[k]["authors"])}. {books[k]["publisher"]}, {books[k]["year"]}. {books[k]["file"]}, беттер: {", ".join(map(str,pss))}.</p>' for k,pss in d['references'].items())
 src+=''.join(f'<p><a href="{esc(x["url"])}">{esc(x["title"])}</a>: {esc(x["use"])}</p>' for x in EXTRA)
 sec('sources','14. Дереккөздер',src+'<p>Түсіндірмелер, тапсырмалар және сызба жаңадан жасалды. Оқулық суреттері көшірілген жоқ. Толық шығу тегі: <a href="sources.json">sources.json</a>.</p>')
 content=f'''<!doctype html><html lang="kk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(d['title'])}</title><style>{CSS}</style></head><body><div class="top"><span>Сабақ прогресі</span><progress id="progress" max="100" value="0" aria-label="Сабақ прогресі"></progress><span id="progress-label">0%</span></div><main><a class="brand" href="../index.html"><img src="../assets/logo.svg" alt="TanymApp логотипі">TanymApp</a><a href="../index.html">← I бөлім</a><p class="meta">{d['code']} · 60 минут · Қазақша</p><h1>{esc(d['title'])}</h1><nav aria-label="Сабақ навигациясы"><a href="#theory">Теория</a><a href="#examples">Мысалдар</a><a href="#practice">Практика</a><a href="#selftest">Тест</a><a href="#cards">Карточкалар</a><a href="#sources">Дереккөздер</a></nav>{''.join(chunks)}<footer><p><a href="lesson.pptx">Презентация</a> · <a href="lesson.pdf">Слайдтар PDF</a> · <a href="textbook.pdf">Оқулық PDF</a> · <a href="teacher_guide.pdf">Мұғалім нұсқаулығы</a></p><p>Серверлік сақтау қосылмаған.</p></footer></main><script id="lesson-data" type="application/json">{json.dumps(d,ensure_ascii=False).replace('</','<\\/')}</script><script>{JS}</script></body></html>'''
 (folder/'lesson.html').write_text(content)

def validate(course):
 assert len({x['code'] for x in course['lessons']})==len(course['lessons'])
 for d in course['lessons']:
  assert len(d['quiz'])>=15
  assert {l:sum(q['level']==l for q in d['quiz']) for l in 'ABC'}==dict(A=5,B=5,C=5)
  assert len({q['id'] for q in d['quiz']})==15
  for q in d['quiz']:
   assert len(q['options'])==len(set(q['options']))==5
   assert 0<=q['answer_index']<5 and len(q['option_explanations'])==5
   assert q['correct_answer']=='ABCDE'[q['answer_index']]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--course',type=Path,default=Path(__file__).with_name('course.json'));ap.add_argument('--out',type=Path,required=True);ap.add_argument('--node',default='node');ap.add_argument('--skip-pptx',action='store_true');ap.add_argument('--soffice',default=os.getenv('COURSE_SOFFICE','soffice'));args=ap.parse_args();course=json.loads(args.course.read_text());validate(course);out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
 for d in course['lessons']:
  folder=out/d['slug'];(folder/'assets').mkdir(parents=True,exist_ok=True)
  (folder/'assets/diagram.svg').write_text(svg(d['diagram']))
  (folder/'quiz.json').write_text(json.dumps(dict(schema_version='1.0',topic_code=d['code'],format='single_choice_5_options',scoring='1 point per first answer, no negative marking',unit_convention=CONVENTION,questions=d['quiz']),ensure_ascii=False,indent=2))
  (folder/'sources.json').write_text(json.dumps(sources(d,course['books']),ensure_ascii=False,indent=2))
  textbook(d,folder,course['books']);teacher(d,folder,course['books']);html_lesson(d,folder,course['books']);print('Built',d['slug'],flush=True)
 links=''.join(f'<section><p>{d["code"]} · 60 минут · 15 тест</p><h2><a href="{d["slug"]}/lesson.html">{html.escape(d["title"])}</a></h2><p>'+html.escape('; '.join(d['goals']))+'</p></section>' for d in course['lessons'])
 (out/'index.html').write_text(f'<!doctype html><html lang="kk"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>ҰБТ информатика • I бөлім</title><style>{CSS}</style><main><p>ҰБТ информатика</p><h1>{html.escape(course["title"])}</h1><p>Бес сабақ. Әрқайсысы 60 минут. Өздігінен оқу және мұғаліммен жеке сабақ.</p>{links}<footer>75 авторлық тест. Барлық материал қазақша. Серверлік сақтау қосылмаған.</footer></main></html>')
 if [d['slug'] for d in course['lessons']]==['01-units','02-conversion','03-memory','04-files','05-archives']:shutil.copyfile(Path(__file__).with_name('home-template.html'),out/'index.html')
 (out/'assets').mkdir(exist_ok=True)
 logo=Path(__file__).with_name('logo.svg')
 shutil.copyfile(logo,out/'assets/logo.svg')
 if not args.skip_pptx:
  subprocess.run([args.node,str(Path(__file__).with_name('build_slides.mjs')),'--course',str(args.course.resolve()),'--out',str(out)],check=True)
  for d in course['lessons']:
   folder=out/d['slug'];subprocess.run([args.soffice,'--headless','--convert-to','pdf','--outdir',str(folder),str(folder/'lesson.pptx')],check=True)
   if not (folder/'lesson.pdf').is_file():raise RuntimeError('Slide PDF export failed: '+d['slug'])
if __name__=='__main__':main()
