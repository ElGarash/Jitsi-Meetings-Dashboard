import { createDbWorker } from 'sql.js-httpvfs';

const workerUrl = 'sqlite.worker.js';
const wasmUrl = 'sql-wasm.wasm';

async function load(sqlQuery) {
	const worker = await createDbWorker(
		[
			{
				from: 'inline',
				config: {
					serverMode: 'full',
					url: '/database.db',
					requestChunkSize: 4096
				}
			}
		],
		workerUrl.toString(),
		wasmUrl.toString()
	);

	const result = await worker.db.query(sqlQuery);

	document.body.textContent = JSON.stringify(result);
}

export default load;
