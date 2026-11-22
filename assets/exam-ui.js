(() => {
  const root = document.getElementById('questions');
  const test = document.getElementById('test');
  if (!root || !test) return;
  let active = 0;
  const panel = document.createElement('div');
  panel.className = 'exam-navigation';
  panel.innerHTML = '<div class="exam-navigation-head"><div><span class="exam-eyebrow">7 СЫНЫП · ИНФОРМАТИКА</span><strong id="exam-current">1 / 40</strong></div><span class="exam-legend"><i></i> Орындалмаған <i></i> Дұрыс <i></i> Қате</span></div><div class="exam-number-list" role="navigation" aria-label="Сұрақ нөмірлері"></div><div class="exam-nav-actions"><button type="button" id="exam-prev">Алдыңғы сұрақ</button><button type="button" id="exam-next">Келесі сұрақ</button></div>';
  root.before(panel);
  const numbers = panel.querySelector('.exam-number-list');
  const current = panel.querySelector('#exam-current');
  const prev = panel.querySelector('#exam-prev');
  const next = panel.querySelector('#exam-next');
  const finish = document.createElement('button');
  finish.type = 'button';
  finish.className = 'exam-finish';
  finish.textContent = 'Тестті аяқтау';
  finish.disabled = true;
  panel.querySelector('.exam-nav-actions').append(finish);
  const analysis = document.createElement('section');
  analysis.className = 'exam-analysis';
  analysis.hidden = true;
  document.getElementById('result')?.after(analysis);
  const section = document.body.dataset.section;
  let sourceQuestions = [];
  fetch('questions.json?v=16').then(r => r.json()).then(data => { sourceQuestions = data.questions; }).catch(() => {});
  const topicNames = {
    1: {'#lesson-1':['Өлшем бірліктері','Единицы измерения','Units of information'],'#lesson-2':['Түрлендіру және көлем','Перевод единиц и объём','Conversion and size'],'#lesson-3':['Компьютер жады','Память компьютера','Computer memory'],'#lesson-4':['Файлдар','Файлы','Files'],'#lesson-5':['Архивтер','Архивы','Archives']},
    2: {'#network':['Компьютерлік желілер','Компьютерные сети','Networks'],'#security':['Қауіпсіздік','Безопасность','Security'],'#interface':['Интерфейс','Интерфейс','Interface']},
    3: {'#basics':['Кесте негіздері','Основы таблиц','Spreadsheet basics'],'#format':['Пішімдеу','Форматирование','Formatting'],'#formulas':['Формулалар','Формулы','Formulas'],'#conditional':['Шартты пішімдеу','Условное форматирование','Conditional formatting'],'#charts':['Диаграммалар','Диаграммы','Charts'],'#models':['Модельдеу','Моделирование','Modeling']},
    4: {'#conditions':['Шарттар','Условия','Conditions'],'#logic':['Логика','Логика','Logic'],'#nested':['Ішкі шарттар','Вложенные условия','Nested conditions'],'#read':['Файлды оқу','Чтение файлов','Reading files'],'#write':['Файлға жазу','Запись файлов','Writing files'],'#errors':['Қателерді талдау','Разбор ошибок','Debugging']}
  };
  function lessonFor(topic) {
    const s = String(topic).toLowerCase();
    if (section === '1') return /жады/.test(s) ? '#lesson-3' : /архив/.test(s) ? '#lesson-5' : /файл/.test(s) ? '#lesson-4' : /түрлен|көлем/.test(s) ? '#lesson-2' : '#lesson-1';
    if (section === '2') return /қауіп/.test(s) ? '#security' : /интерфейс/.test(s) ? '#interface' : '#network';
    if (section === '3') return /диаграм/.test(s) ? '#charts' : /шартты/.test(s) ? '#conditional' : /формул/.test(s) ? '#formulas' : /пішім/.test(s) ? '#format' : '#basics';
    return /файл/.test(s) ? '#read' : /қате/.test(s) ? '#errors' : /логик/.test(s) ? '#logic' : '#conditions';
  }
  const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function renderAnalysis() {
    const cards = [...root.querySelectorAll('.question')];
    if (!cards.length || !sourceQuestions.length) return;
    const lang = document.documentElement.lang;
    const labels = lang === 'ru' ? {title:'Результат по темам', correct:'Верно', review:'Повторить тему', good:'Тема освоена', score:'Правильных ответов'} : lang === 'en' ? {title:'Results by topic',correct:'Correct',review:'Review this topic',good:'Topic mastered',score:'Correct answers'} : {title:'Тақырыптар бойынша нәтиже',correct:'Дұрыс',review:'Тақырыпты қайталау',good:'Тақырып меңгерілген',score:'Дұрыс жауап'};
    const groups = new Map();
    cards.forEach((card, index) => {
      const source = sourceQuestions[index];
      if (!source) return;
      let anchor = lessonFor(source.topic);
      if (index >= 25 && index <= 29) {
        const contexts = {1:['#lesson-1','#lesson-1','#lesson-1','#lesson-3','#lesson-5'],2:['#network','#network','#network','#network','#security'],3:['#formulas','#basics','#formulas','#formulas','#formulas'],4:['#read','#read','#logic','#conditions','#logic']};
        anchor = contexts[section][index - 25];
      }
      const group = groups.get(anchor) || {total:0, correct:0, anchor};
      group.total++;
      if (card.querySelector('.feedback.show.good')) group.correct++;
      groups.set(anchor, group);
    });
    const total = [...groups.values()].reduce((n, g) => n + g.correct, 0);
    analysis.innerHTML = `<h2>${labels.title}</h2><p class="exam-analysis-score">${labels.score}: <strong>${total} / ${cards.length}</strong></p><div class="exam-analysis-grid">${[...groups].map(([anchor,g]) => {
      const percent = Math.round(g.correct / g.total * 100);
      const needsReview = g.correct < g.total;
      const name = topicNames[section]?.[anchor]?.[lang === 'ru' ? 1 : lang === 'en' ? 2 : 0] || anchor;
      return `<article class="${needsReview?'review':''}"><div><strong>${escape(name)}</strong><span>${g.correct}/${g.total}</span></div><div class="exam-analysis-track"><i style="width:${percent}%"></i></div><a href="${g.anchor}">${needsReview?labels.review:labels.good}</a></article>`;
    }).join('')}</div>`;
    analysis.hidden = false;
    analysis.scrollIntoView({behavior:'smooth',block:'start'});
  }
  finish.addEventListener('click', renderAnalysis);
  document.addEventListener('change', event => { if (event.target.matches('.language-picker select') && !analysis.hidden) queueMicrotask(renderAnalysis); });

  function update() {
    const cards = [...root.querySelectorAll('.question')];
    if (!cards.length) return;
    active = Math.max(0, Math.min(active, cards.length - 1));
    cards.forEach((card, i) => {
      card.hidden = i !== active;
      card.classList.toggle('exam-active-question', i === active);
    });
    root.querySelector('.context-card')?.classList.toggle('context-active', active >= 25 && active <= 29);
    if (numbers.children.length !== cards.length) {
      numbers.replaceChildren(...cards.map((_, i) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.textContent = String(i + 1);
        button.title = `${i + 1}-сұрақ`;
        button.setAttribute('aria-label', `${i + 1}-сұрақ`);
        button.dataset.question = String(i);
        return button;
      }));
    }
    [...numbers.children].forEach((button, i) => {
      const feedback = cards[i].querySelector('.feedback.show');
      const done = !!feedback;
      const wrong = done && !feedback.classList.contains('good');
      button.classList.toggle('answered', done && !wrong);
      button.classList.toggle('incorrect', wrong);
      button.classList.toggle('current', i === active);
      button.setAttribute('aria-current', i === active ? 'step' : 'false');
      button.setAttribute('aria-label', `${i + 1}-сұрақ · ${wrong ? 'қате' : done ? 'орындалған' : 'орындалмаған'}`);
    });
    current.textContent = `${active + 1} / ${cards.length}`;
    prev.disabled = active === 0;
    next.disabled = active === cards.length - 1;
    finish.disabled = cards.some(card => !card.querySelector('.feedback.show'));
    const selected = numbers.children[active];
    if (selected) {
      if (selected.offsetLeft < numbers.scrollLeft) numbers.scrollLeft = selected.offsetLeft;
      else if (selected.offsetLeft + selected.offsetWidth > numbers.scrollLeft + numbers.clientWidth) numbers.scrollLeft = selected.offsetLeft + selected.offsetWidth - numbers.clientWidth;
    }
  }
  function go(index) {
    active = index;
    update();
    panel.scrollIntoView({ block: 'start', behavior: 'smooth' });
  }
  numbers.addEventListener('click', event => {
    const button = event.target.closest('[data-question]');
    if (button) go(Number(button.dataset.question));
  });
  prev.addEventListener('click', () => go(active - 1));
  next.addEventListener('click', () => go(active + 1));
  root.addEventListener('click', event => {
    if (event.target.closest('[data-check]')) queueMicrotask(update);
  });
  document.getElementById('reset')?.addEventListener('click', () => queueMicrotask(() => { active = 0; update(); }));
  new MutationObserver(records => {
    if (records.some(record => record.target === root)) { active = 0; analysis.hidden = true; update(); }
    else if (records.some(record => record.target.classList?.contains('feedback'))) update();
  }).observe(root, { childList: true, attributes: true, attributeFilter: ['class'], subtree: true });
  update();
})();
