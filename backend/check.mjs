import fs from 'fs';
import { transformSync } from '@babel/core';

// extract JSX
const html = fs.readFileSync('../k1-dashboard.html', 'utf8');
const match = html.match(/<script type="text\/babel">([\s\S]*?)<\/script>/);

if (match) {
  try {
    transformSync(match[1], { presets: ['@babel/preset-react'] });
    console.log('Valid JSX');
  } catch (err) {
    console.error('Syntax error:', err.message);
  }
} else {
  console.log('No script found');
}
