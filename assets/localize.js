(() => {
  const script = document.currentScript;
  const originalText = new WeakMap();
  const translatedText = new WeakMap();
  const attributes = ['alt', 'title', 'placeholder', 'aria-label'];
  const ignored = new Set(['SCRIPT', 'STYLE', 'CODE', 'PRE', 'SVG', 'TEXTAREA']);
  const originalTitle = document.title;
  let dictionary = {};
  let language = 'kk';
  try { language = localStorage.getItem('tanymapp-language') || 'kk'; } catch { /* Storage disabled. */ }
  if (!['kk', 'ru', 'en'].includes(language)) language = 'kk';
  document.documentElement.lang = language;

  const picker = document.createElement('label');
  picker.className = 'language-picker';
  picker.innerHTML = '<span>🌐</span><select aria-label="Тіл / Язык / Language"><option value="kk">Қазақша</option><option value="ru">Русский</option><option value="en">English</option></select>';
  picker.querySelector('select').value = language;
  document.querySelector('.bar')?.append(picker);

  function dynamicTranslation(key) {
    if (language === 'kk') return null;
    const option = key.match(/^([A-F]\.\s*)(.+)$/);
    if (option) return option[1] + (dictionary[option[2]]?.[language] || option[2]);
    const questionLabel = key.match(/^(\d+)-сұрақ(?: · (орындалған|орындалмаған|қате))?$/);
    if (questionLabel) return language === 'ru' ? `Вопрос ${questionLabel[1]}${questionLabel[2] ? ' · ' + dictionary[questionLabel[2]][language] : ''}` : `Question ${questionLabel[1]}${questionLabel[2] ? ' · ' + dictionary[questionLabel[2]][language] : ''}`;
    if (key === 'Ортақ контекст · 26–30 сұрақ') return language === 'ru' ? 'Общий контекст · вопросы 26–30' : 'Shared context · questions 26–30';
    const meta = key.match(/^(.+?) · ([ABC])(?: деңгейі)? · (Бір жауап|Бірнеше жауап|Сәйкестік)$/);
    if (meta) {
      const topic = dictionary[meta[1]]?.[language] || meta[1];
      const kind = dictionary[meta[3]]?.[language] || meta[3];
      const level = language === 'ru' ? `уровень ${meta[2]}` : `level ${meta[2]}`;
      return `${topic} · ${level} · ${kind}`;
    }
    const progress = key.match(/^(\d+)\s*\/\s*40 жауап(?: берілді)?$/);
    if (progress) return language === 'ru' ? `${progress[1]} / 40 отвечено` : `${progress[1]} / 40 answered`;
    const practiceProgress = key.match(/^(\d+)\s*\/\s*5 қадам тексерілді(.*)$/);
    if (practiceProgress) return language === 'ru' ? `${practiceProgress[1]} / 5 шагов проверено` : `${practiceProgress[1]} / 5 steps checked`;
    const result = key.match(/^Нәтиже:\s*(\d+)\s*\/\s*40\.?\s*(.*)$/);
    if (result) {
      const message = dictionary[result[2]]?.[language] || result[2];
      return language === 'ru' ? `Результат: ${result[1]} / 40. ${message}` : `Result: ${result[1]} / 40. ${message}`;
    }
    return null;
  }

  function textNode(node) {
    if (node.parentElement && (ignored.has(node.parentElement.tagName) || node.parentElement.closest('code,pre,script,style,svg,textarea'))) return;
    let original = originalText.get(node);
    if (original === undefined || (node.nodeValue !== original && node.nodeValue !== translatedText.get(node))) {
      original = node.nodeValue;
      originalText.set(node, original);
    }
    const key = original.trim();
    const translated = language === 'kk' ? null : dynamicTranslation(key) || dictionary[key]?.[language];
    const replacement = translated ? original.replace(key, translated) : original;
    translatedText.set(node, replacement);
    if (node.nodeValue !== replacement) node.nodeValue = replacement;
  }
  function elementAttributes(element) {
    if (element.tagName === 'IMG') {
      const current = element.getAttribute('src') || '';
      const base = element.dataset.i18nOriginalSrc || current;
      if (/\/(?:network-scale-clear|cables-clean|cell-format-clear|conditional-clear|formula-clear|excel-interface-clear|chart-insert-clear)\.svg$/.test(base)) {
        element.dataset.i18nOriginalSrc = base;
        const localized = language === 'kk' ? base : base.replace(/\.svg$/, `.${language}.svg`);
        if (current !== localized) element.setAttribute('src', localized);
      }
    }
    for (const attribute of attributes) {
      if (!element.hasAttribute(attribute)) continue;
      const record = `i18nOriginal${attribute.replace(/-([a-z])/g, (_, c) => c.toUpperCase()).replace(/^./, c => c.toUpperCase())}`;
      const translatedRecord = `${record}Translated`;
      let original = element.dataset[record];
      if (!original || (element.getAttribute(attribute) !== original && element.getAttribute(attribute) !== element.dataset[translatedRecord])) {
        original = element.getAttribute(attribute);
        element.dataset[record] = original;
      }
      const replacement = language === 'kk' ? original : dynamicTranslation(original) || dictionary[original]?.[language] || original;
      element.dataset[translatedRecord] = replacement;
      if (element.getAttribute(attribute) !== replacement) element.setAttribute(attribute, replacement);
    }
  }
  function translate(root) {
    if (root.nodeType === Node.TEXT_NODE) { textNode(root); return; }
    if (root.nodeType !== Node.ELEMENT_NODE || ignored.has(root.tagName)) return;
    elementAttributes(root);
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT);
    while (walker.nextNode()) {
      if (walker.currentNode.nodeType === Node.TEXT_NODE) textNode(walker.currentNode);
      else if (!ignored.has(walker.currentNode.tagName)) elementAttributes(walker.currentNode);
    }
  }
  picker.querySelector('select').addEventListener('change', event => {
    language = event.target.value;
    document.documentElement.lang = language;
    try { localStorage.setItem('tanymapp-language', language); } catch { /* Storage disabled. */ }
    translate(document.body);
    document.title = language === 'kk' ? originalTitle : dictionary[originalTitle]?.[language] || originalTitle;
  });
  const observer = new MutationObserver(records => {
    for (const record of records) {
      if (record.type === 'characterData') translate(record.target);
      else if (record.type === 'attributes') elementAttributes(record.target);
      else for (const node of record.addedNodes) translate(node);
    }
  });
  observer.observe(document.body, { childList: true, characterData: true, attributes: true, attributeFilter: attributes, subtree: true });
  fetch(new URL('i18n.json?v=16', script.src)).then(response => response.json()).then(data => {
    dictionary = data;
    translate(document.body);
    document.title = language === 'kk' ? originalTitle : dictionary[originalTitle]?.[language] || originalTitle;
  }).catch(() => { /* The Kazakh original remains readable if translations cannot load. */ });
})();
