/* Keep one option order for an attempt so a page reload preserves saved answers. */
window.TanymQuiz = (() => {
  const randomIndex = length => {
    if (globalThis.crypto?.getRandomValues) {
      const value = new Uint32Array(1);
      crypto.getRandomValues(value);
      return value[0] % length;
    }
    return Math.floor(Math.random() * length);
  };
  const shuffledIndices = length => {
    const indices = Array.from({ length }, (_, i) => i);
    for (let i = length - 1; i > 0; i--) {
      const j = randomIndex(i + 1);
      [indices[i], indices[j]] = [indices[j], indices[i]];
    }
    return indices;
  };
  const isPermutation = (order, length) => Array.isArray(order) &&
    order.length === length && new Set(order).size === length &&
    order.every(i => Number.isInteger(i) && i >= 0 && i < length);
  const storageKey = section => `tanymapp-option-order-${section}-${section === '1' ? 'v3' : 'v2'}`;

  function createOrders(questions) {
    const correctPositions = [];
    return questions.map(q => {
      if (q.type === 'match') return shuffledIndices(q.targets.length);
      if (q.type === 'multi') {
        let order, positions;
        do {
          order = shuffledIndices(q.options.length);
          positions = q.answer.map(answer => order.indexOf(answer)).sort((a, b) => a - b);
        } while (positions.length === 3 && positions[2] - positions[0] === 2);
        return order;
      }
      const length = q.options.length;
      const lowest = Math.min(...Array.from({ length }, (_, i) => correctPositions[i] || 0));
      const candidates = Array.from({ length }, (_, i) => i).filter(i => (correctPositions[i] || 0) === lowest);
      const slot = candidates[randomIndex(candidates.length)];
      correctPositions[slot] = (correctPositions[slot] || 0) + 1;
      const order = shuffledIndices(length);
      const current = order.indexOf(q.answer);
      [order[current], order[slot]] = [order[slot], order[current]];
      return order;
    });
  }

  function prepare(questions, section, fresh = false) {
    const key = storageKey(section);
    let orders;
    if (!fresh) {
      try { orders = JSON.parse(localStorage.getItem(key)); } catch { /* Generate below. */ }
    }
    const valid = Array.isArray(orders) && orders.length === questions.length &&
      orders.every((order, i) => isPermutation(order,
        questions[i].type === 'match' ? questions[i].targets.length : questions[i].options.length));
    if (!valid) {
      orders = createOrders(questions);
      try { localStorage.setItem(key, JSON.stringify(orders)); } catch { /* Private browsing. */ }
    }
    return questions.map((q, i) => {
      const order = orders[i];
      if (q.type === 'match') return { ...q, targets: order.map(j => q.targets[j]) };
      const copy = { ...q, options: order.map(j => q.options[j]) };
      copy.answer = q.type === 'single' ? order.indexOf(q.answer) : q.answer.map(j => order.indexOf(j)).sort((a, b) => a - b);
      return copy;
    });
  }
  return { prepare };
})();
