/**
 * _s220_retryBudget.ts — proves the RPC retry is bounded by TIME, not attempt count.
 *
 * OFFLINE. Stubs globalThis.fetch; makes no network call and reads no live data.
 *
 * The three behaviours that must hold together:
 *   1. the cold-start retry the original code existed for is PRESERVED
 *   2. a 57014 that already burned the whole budget is NOT retried
 *   3. a non-57014 error still fails fast
 *
 * USAGE (from backend/):  node_modules/.bin/tsx scripts/_s220_retryBudget.ts
 */
process.env.SUPABASE_URL ||= 'https://stub.supabase.co';
process.env.SUPABASE_ANON_KEY ||= 'stub-anon-key';
process.env.SUPABASE_SERVICE_KEY ||= 'stub-service-key';

const { searchWikiRoutedExact } = await import('../src/lib/wikiRepository.js');

const TIMEOUT_BODY = '{"code":"57014","message":"canceling statement due to statement timeout"}';
const vec = new Array(1536).fill(0.01);
const embedFn = async () => vec;

type Script = Array<{ delayMs: number; status: number; body: string }>;
let attempts = 0;

function stub(script: Script) {
  attempts = 0;
  globalThis.fetch = (async () => {
    const step = script[Math.min(attempts, script.length - 1)];
    attempts++;
    if (step.delayMs) await new Promise((r) => setTimeout(r, step.delayMs));
    return {
      ok: step.status === 200,
      status: step.status,
      text: async () => step.body,
    } as any;
  }) as any;
}

async function run(label: string, script: Script, expectAttempts: number, expectThrow: boolean) {
  stub(script);
  const t0 = Date.now();
  let threw = false;
  try {
    await searchWikiRoutedExact('q', embedFn as any, { sourceIds: ['g04'], topK: 8, queryVec: vec });
  } catch {
    threw = true;
  }
  const ms = Date.now() - t0;
  const ok = attempts === expectAttempts && threw === expectThrow;
  console.log(
    `  ${ok ? 'PASS' : 'FAIL'}  ${label}\n` +
    `          嘗試 ${attempts} 次（預期 ${expectAttempts}）· ${threw ? '拋錯' : '成功'}（預期 ${expectThrow ? '拋錯' : '成功'}）· 共 ${ms}ms`
  );
  return ok;
}

const results: boolean[] = [];

// 1. Cold-start blip: first attempt times out FAST, second succeeds. Must still retry.
results.push(await run(
  '冷啟動閃斷：首次快速 57014，第二次成功 → 重試必須保留',
  [{ delayMs: 100, status: 500, body: TIMEOUT_BODY }, { delayMs: 10, status: 200, body: '[]' }],
  2, false
));

// 2. Budget already spent: one attempt consumed the whole 6s deadline. Must NOT retry.
results.push(await run(
  '預算已耗盡：單次 57014 已用掉 6 秒預算 → 不得再重試',
  [{ delayMs: 6100, status: 500, body: TIMEOUT_BODY }],
  1, true
));

// 3. Non-57014 still fails fast, unchanged.
results.push(await run(
  '非 57014 錯誤 → 即時失敗，行為不變',
  [{ delayMs: 10, status: 400, body: '{"code":"42P01","message":"no such table"}' }],
  1, true
));

// 4. Fast repeated timeouts still get all three attempts (what the count protected).
results.push(await run(
  '連續快速 57014 → 仍可用盡三次嘗試',
  [{ delayMs: 50, status: 500, body: TIMEOUT_BODY }],
  3, true
));

console.log(results.every(Boolean) ? '\n  ALL PASS\n' : '\n  FAILED\n');
process.exit(results.every(Boolean) ? 0 : 1);
