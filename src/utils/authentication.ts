import createAuth0Client from '@auth0/auth0-spa-js';
import { user, isAuthenticated, popupOpen, accessTokenStore } from '../utils/stores';

async function createClient() {
	const auth0Client = await createAuth0Client({
		domain: 'elgarash.us.auth0.com',
		client_id: 'vV2NGwEyc9tL75dBW9017SBR8oqhAzWA',
		audience: 'AzureServerlessFunction'
	});

	return auth0Client;
}

async function loginWithPopup(client) {
	popupOpen.set(true);
	try {
		await client.loginWithPopup();
		user.set(await client.getUser());
		accessTokenStore.set(await client.getTokenSilently());
		isAuthenticated.set(true);
	} catch (e) {
		// eslint-disable-next-line
		console.error(e);
	} finally {
		popupOpen.set(false);
	}
}

function logout(client) {
	isAuthenticated.set(false);
	user.set(null);
	accessTokenStore.set(null);
	return client.logout({
		returnTo: 'http://localhost:3000/'
	});
}

const auth = {
	createClient,
	loginWithPopup,
	logout
};

export default auth;
