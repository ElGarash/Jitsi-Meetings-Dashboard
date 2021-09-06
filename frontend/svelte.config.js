import preprocess from 'svelte-preprocess';
import adapter from '@sveltejs/adapter-static';
import copy from 'rollup-plugin-copy';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  // Consult https://github.com/sveltejs/svelte-preprocess
  // for more information about preprocessors
  preprocess: preprocess(),
  kit: {
    vite: {
      plugins: [
        copy({
          targets: [
            {
              src: [
                './node_modules/sql.js-httpvfs/dist/sqlite.worker.js',
                './node_modules/sql.js-httpvfs/dist/sql-wasm.wasm'
              ],
              dest: './static'
            }
          ],
          verbose: true,
          hook: 'buildStart' // Required for dev mode.
        })
      ]
    },
    adapter: adapter(),
    // hydrate the <div id="svelte"> element in src/app.html
    target: '#svelte'
    // paths: {
    // 	base: '/meetings'  // Gonna need this when bundling the app to GitHub Pages.
    // }
  }
};

export default config;
