import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const args=process.argv.slice(2);const get=k=>args[args.indexOf(k)+1];
const course=JSON.parse(await fs.readFile(get('--course'),'utf8'));const out=path.resolve(get('--out'));
const moduleRoot=process.env.COURSE_NODE_MODULES;
if(moduleRoot)process.env.RUNTIME_NODE_MODULES=moduleRoot;
const {Presentation,PresentationFile}=moduleRoot?await import(pathToFileURL(path.join(moduleRoot,'@oai/artifact-tool/dist/artifact_tool.mjs')).href):await import('@oai/artifact-tool');
const font='Times New Roman';const manifest=[];
for(const d of course.lessons){
 const presentation=Presentation.create({slideSize:{width:1280,height:720}});const records=[];
 function box(slide,text,x,y,w,h,size=30,bold=false){const b=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});b.text=text;b.text.style={typeface:font,fontSize:size,color:'#000000',bold};return b;}
 function add(title,body='',notes='',kind='text'){
  const s=presentation.slides.add();s.background.fill='#FFFFFF';box(s,title,64,42,1152,112,44,true);if(body)box(s,body,66,190,1148,430,31);
  box(s,d.code+'  •  '+(presentation.slides.items.length),65,670,1100,26,17);
  s.speakerNotes.text=notes||d.title;records.push({title,body,kind});return s;
 }
 add(d.title,d.goals.join('\n\n'),'60 минут. '+d.prerequisites.join('; '));
 for(const sec of d.sections){
  let sentences=sec.text.match(/[^.!?]+[.!?]+|[^.!?]+$/g)||[sec.text];let short=sentences.slice(0,3).join(' ').trim();
  if(short.length>570)short=sentences.slice(0,2).join(' ').trim();
  add(sec.title,short,sec.text+'\nДереккөз: '+sec.source);
 }
 const diagramSlide=add('Негізгі байланыстар','',d.diagram_caption,'diagram');
 d.diagram.forEach((t,i)=>{
  const x=66+i*290;const b=diagramSlide.shapes.add({geometry:'rect',position:{left:x,top:240,width:265,height:120},fill:'#FFFFFF',line:{fill:'#000000',width:1}});b.text=t;b.text.style={typeface:font,fontSize:26,color:'#000000',alignment:'center',verticalAlignment:'middle'};
  if(i<3)diagramSlide.shapes.add({geometry:'rightArrow',position:{left:x+266,top:292,width:23,height:14},fill:'#000000',line:{fill:'#000000',width:0}});
 });box(diagramSlide,d.diagram_caption,66,430,1148,170,27);
 const ts=add('Салыстыру кестесі','',d.sections.map(s=>s.source).join('\n'),'table');
 const t=ts.tables.add({rows:d.table.length,columns:d.table[0].length,left:66,top:180,width:1148,height:405,values:d.table});
 t.borders.assign({fill:'#000000',width:1,style:'solid'});
 for(let r=0;r<d.table.length;r++)for(let c=0;c<d.table[0].length;c++){const cell=t.getCell(r,c);cell.fill='#FFFFFF';cell.text.style={typeface:font,fontSize:25,bold:r===0,color:'#000000'};}
 for(let i=0;i<d.examples.length;i++){const ex=d.examples[i];add('Мысал '+(i+1),ex.question,'Алдымен оқушының шешімін тыңдаңыз. Авторлық мысал.','question');add('Шешімі',ex.steps.map((x,j)=>(j+1)+'. '+x).join('\n\n'),'Авторлық шешім. '+d.sections.map(s=>s.source).join('; '),'answer');}
 for(const p of d.practice){add(p.level+' деңгейі: тапсырма',p.question,'Оқушы өз бетінше орындайды. Авторлық тапсырма.','question');add(p.level+' деңгейі: жауап',p.answer,'Авторлық шешім. Қате болса, тиісті теорияға оралыңыз.','answer');}
 add('Қорытынды',d.summary.join('\n\n'),d.errors.join('\n'));
 const refs=Object.entries(d.references).map(([k,pages])=>`${k}: ${course.books[k].publisher}, ${course.books[k].year}; ${course.books[k].file}, ${pages.join(', ')}-беттер.`);
 add('Дереккөздер',refs.join('\n\n'),'Оқулық суреттері мен тапсырмалары көшірілген жоқ. Барлық сызбалар мен есептер осы сабаққа жасалды. E1: https://physics.nist.gov/cuu/Units/binary.html; E2: https://www.unicode.org/faq/utf_bom.html');
 const build=path.resolve(process.env.COURSE_BUILD_DIR||path.join(out,'..','..','work','slides'));await fs.mkdir(path.join(build,d.slug),{recursive:true});const candidate=path.join(build,d.slug,'candidate.pptx');await(await PresentationFile.exportPptx(presentation)).save(candidate);
 const final=path.join(out,d.slug,'lesson.pptx');
 if(process.env.COURSE_PRESENTATION_SKILL){const skill=process.env.COURSE_PRESENTATION_SKILL;const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
  await finalizePresentation({workspaceDir:path.resolve(out,'../..'),candidatePath:candidate,finalPath:final,pythonExecutable:process.env.COURSE_PYTHON||'python3',integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit','--require-native-table-slide','7'],requiredNativeTableOwnerSlides:[7],fontPolicy:{basis:'user_request',families:[font]},verifyArtifactToolImport:true,receiptPath:path.join(build,d.slug,'validation.json')});
 }else{await fs.copyFile(candidate,final);}
 await fs.writeFile(path.join(build,d.slug,'slides.json'),JSON.stringify(records,null,2));
 manifest.push({slug:d.slug,slides:records.length,pptx:d.slug+'/lesson.pptx'});console.log('PPTX',d.slug,records.length);
}
await fs.mkdir(path.join(out,'generator'),{recursive:true});
await fs.writeFile(path.join(out,'generator','slide-manifest.json'),JSON.stringify(manifest,null,2));
