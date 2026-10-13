// Offline self-test for notify_new_items.js (S238). Run: node .github/scripts/notify_new_items.test.js
// Mocks the three GitHub REST calls; asserts WHEN Leonard is notified, not wording.
const assert = require('assert');
const notify = require('./notify_new_items.js');
const { MENTION } = notify._internal;

function mockGithub(openIssue) {
  const calls = [];
  let issue = openIssue ? { ...openIssue } : null;
  const github = { rest: { issues: {
    listForRepo: async () => ({ data: issue ? [issue] : [] }),
    create: async a => { calls.push(['create', a]); issue = { number: 99, body: a.body }; return { data: { number: 99 } }; },
    update: async a => { calls.push(['update', a]); issue.body = a.body; return {}; },
    createComment: async a => { calls.push(['comment', a]); return {}; },
  } } };
  return { github, calls, current: () => issue };
}
const context = { repo: { owner: 'o', repo: 'r' }, runId: 1, serverUrl: 'https://github.com' };
const core = { info: () => {} };
const base = { context, core, label: 'l', title: 't', body: 'report', headline: n => `新 ${n}`, action: '處理' };
const items = keys => keys.map(k => ({ key: k, text: k }));

(async () => {
  // 1. No open issue -> created, body @mentions (a NEW issue with a mention notifies).
  let m = mockGithub(null);
  let r = await notify({ ...base, github: m.github, items: items(['a', 'b']) });
  assert.equal(r.announced, 2);
  assert.equal(m.calls[0][0], 'create');
  assert.ok(m.calls[0][1].body.startsWith(MENTION), 'new issue must start with the mention');

  // 2. Same items next week -> body updated, NO comment (nothing new).
  r = await notify({ ...base, github: m.github, items: items(['a', 'b']) });
  assert.equal(r.announced, 0);
  assert.deepEqual(m.calls.map(c => c[0]), ['create', 'update']);

  // 3. One new item -> a comment that mentions and lists ONLY the new one.
  r = await notify({ ...base, github: m.github, items: items(['a', 'b', 'c']) });
  assert.equal(r.announced, 1);
  const comment = m.calls[m.calls.length - 1];
  assert.equal(comment[0], 'comment');
  assert.ok(comment[1].body.startsWith(MENTION));
  assert.ok(comment[1].body.includes('- c') && !comment[1].body.includes('- a'));
  assert.ok(comment[1].body.includes('另有 2 項早前已通知'));

  // 4. An item drops off and comes back while the issue stays open -> not re-announced.
  await notify({ ...base, github: m.github, items: items(['a', 'c']) });
  const before = m.calls.length;
  r = await notify({ ...base, github: m.github, items: items(['a', 'b', 'c']) });
  assert.equal(r.announced, 0);
  assert.equal(m.calls.slice(before).filter(c => c[0] === 'comment').length, 0);

  // 5. Pre-S238 issue (no marker in body, e.g. freshness #1) -> everything announced once.
  m = mockGithub({ number: 1, body: 'old body without marker' });
  r = await notify({ ...base, github: m.github, items: items(['x', 'y']) });
  assert.equal(r.announced, 2);
  assert.deepEqual(m.calls.map(c => c[0]), ['update', 'comment']);

  // 6. Keys with spaces / non-ASCII survive the marker round-trip.
  m = mockGithub(null);
  const odd = ['https://e.x/a b.pdf', '學校|error', 'x-->y'];
  await notify({ ...base, github: m.github, items: items(odd) });
  r = await notify({ ...base, github: m.github, items: items(odd) });
  assert.equal(r.announced, 0);

  console.log('notify_new_items: ALL PASS (6 cases)');
})().catch(e => { console.error(e); process.exit(1); });
