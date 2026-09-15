import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = process.cwd();
const dist = resolve(root, 'dist');
const www = resolve(root, 'www');
if (!existsSync(resolve(dist, 'index.html'))) {
  throw new Error('dist/index.html is missing. Run npm run build:web first.');
}
rmSync(www, { recursive: true, force: true });
mkdirSync(www, { recursive: true });
cpSync(dist, www, { recursive: true });
writeFileSync(resolve(www, 'cordova-bootstrap.js'), 'window.__CORDOVA_BUILD__ = true;\n', 'utf8');
const indexPath = resolve(www, 'index.html');
let html = readFileSync(indexPath, 'utf8');
const injection = '<script src="cordova.js"></script><script src="cordova-bootstrap.js"></script>';
if (!html.includes('cordova-bootstrap.js')) {
  html = html.replace('</head>', `${injection}</head>`);
}
writeFileSync(indexPath, html, 'utf8');
console.log(`Cordova web assets synchronized to ${www}`);
