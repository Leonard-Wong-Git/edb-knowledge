// Shared "tell Leonard about NEW items" step for the detection monitors (S238).
//
// Why this exists: until S238 every monitor kept ONE open issue and, on later
// runs, only EDITED its body. GitHub does not send a notification for a body
// edit, and Leonard does not watch this repo, so only an @mention in a NEW
// issue or a NEW comment ever reaches his inbox. The freshness issue (#1) was
// opened on 2026-06-08 without a mention and then edited weekly: four months,
// 29 changed sources, zero notifications.
//
// Contract (Leonard, S238): notify only when something NEW appears — no digest,
// no reminders for items he has already been told about.
//   * The issue body still carries the full current list (engineering detail).
//   * A hidden marker in the body records the item keys already announced.
//   * Items whose key is not in the marker are "new": a fresh issue (mention in
//     the body) or a NEW comment (mention) announces them in plain Chinese.
//
// Usage from actions/github-script (after actions/checkout):
//   const notify = require(`${process.env.GITHUB_WORKSPACE}/.github/scripts/notify_new_items.js`);
//   await notify({ github, context, core, label, title, body, items, headline, action });
// items: [{ key: string, text: string }] — the FULL current list.

const MENTION = '@Leonard-Wong-Git';
const MARKER_RE = /<!-- notify-keys:([A-Za-z0-9+/=]*) -->/;
const MAX_LISTED = 20;

function readKeys(body) {
  const m = MARKER_RE.exec(body || '');
  if (!m) return null;                       // never announced through this helper
  try {
    return new Set(JSON.parse(Buffer.from(m[1], 'base64').toString('utf8')));
  } catch (e) {
    return null;
  }
}

function writeKeys(keys) {
  const b64 = Buffer.from(JSON.stringify([...keys]), 'utf8').toString('base64');
  return `<!-- notify-keys:${b64} -->`;
}

function announcement({ fresh, total, headline, action, runUrl }) {
  const shown = fresh.slice(0, MAX_LISTED).map(i => `- ${i.text}`).join('\n');
  const more = fresh.length > MAX_LISTED ? `\n- ……另有 ${fresh.length - MAX_LISTED} 項，見上方 Issue 內文` : '';
  const older = total - fresh.length;
  return [
    MENTION,
    '',
    `**${headline(fresh.length)}**`,
    '',
    shown + more,
    '',
    `**要你做的事：**${action}`,
    older > 0 ? `\n（另有 ${older} 項早前已通知、仍未處理，不再重複列出。）` : '',
    runUrl ? `\n詳細報告：${runUrl}` : '',
  ].join('\n');
}

async function notifyNewItems({ github, context, core, label, title, body, items, headline, action }) {
  const { owner, repo } = context.repo;
  const runUrl = `${context.serverUrl || 'https://github.com'}/${owner}/${repo}/actions/runs/${context.runId}`;
  const keys = new Set(items.map(i => i.key));
  const open = (await github.rest.issues.listForRepo({ owner, repo, state: 'open', labels: label })).data;
  const existing = open[0];

  const seen = existing ? (readKeys(existing.body) || new Set()) : new Set();
  const fresh = items.filter(i => !seen.has(i.key));
  // Keep every key ever announced while the issue stays open, so an item that
  // drops off for a week and comes back is not re-announced as new.
  const remembered = new Set([...seen, ...keys]);
  const fullBody = `${body}\n\n${writeKeys(remembered)}`;

  if (!existing) {
    const head = fresh.length ? announcement({ fresh, total: items.length, headline, action, runUrl }) : '';
    const created = await github.rest.issues.create({
      owner, repo, title, labels: [label],
      body: head ? `${head}\n\n---\n\n${fullBody}` : fullBody,
    });
    core.info(`Created #${created.data.number}; announced ${fresh.length} new item(s).`);
    return { issue: created.data.number, announced: fresh.length };
  }

  await github.rest.issues.update({ owner, repo, issue_number: existing.number, title, body: fullBody });
  if (fresh.length) {
    await github.rest.issues.createComment({
      owner, repo, issue_number: existing.number,
      body: announcement({ fresh, total: items.length, headline, action, runUrl }),
    });
    core.info(`Updated #${existing.number}; announced ${fresh.length} new item(s) in a comment.`);
  } else {
    core.info(`Updated #${existing.number}; nothing new, no notification.`);
  }
  return { issue: existing.number, announced: fresh.length };
}

module.exports = notifyNewItems;
module.exports._internal = { readKeys, writeKeys, announcement, MENTION };
