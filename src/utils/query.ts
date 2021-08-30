import { createDbWorker } from 'sql.js-httpvfs';

const workerUrl = 'sqlite.worker.js';
const wasmUrl = 'sql-wasm.wasm';

async function query(sqlQuery) {
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

	return await worker.db.query(sqlQuery);
}

export default query;
