// src/auth.js

import { onMount } from 'svelte';
import createAuth0Client from '@auth0/auth0-spa-js';
import { authError, isAuthenticated, isLoading, userInfo, authToken } from '../utils/stores';

// Default Auth0 expiration time is 10 hours or something like that.
// If you want to get fancy you can parse the JWT token and get
// token's actual expiration time.
const refreshRate = 10 * 60 * 60 * 1000;

export function createAuth(config) {
	let auth0 = null;
	let intervalId = undefined;

	// You can use Svelte's hooks in plain JS files. How nice!
	onMount(async () => {
		auth0 = await createAuth0Client(config);

		// Not all browsers support this, please program defensively!
		const params = new URLSearchParams(window.location.search);

		// Check if something went wrong during login redirect
		// and extract the error message
		if (params.has('error')) {
			authError.set(new Error(params.get('error_description')));
		}

		// if code then login success
		if (params.has('code')) {
			// Let the Auth0 SDK do it's stuff - save some state, etc.
			await auth0.handleRedirectCallback();
			// Can be smart here and redirect to original path instead of root
			window.history.replaceState({}, document.title, '/');
			authError.set(null);
		}

		const _isAuthenticated = await auth0.isAuthenticated();
		isAuthenticated.set(_isAuthenticated);

		if (_isAuthenticated) {
			// while on it, fetch the user info
			userInfo.set(await auth0.getUser());

			// Get the access token. Make sure to supply audience property
			// in Auth0 config, otherwise you will soon start throwing stuff!
			authToken.set(await auth0.getTokenSilently());

			// refresh token after specific period or things will stop
			// working. Useful for long-lived apps like dashboards.
			intervalId = setInterval(async () => {
				authToken.set(await auth0.getTokenSilently());
			}, refreshRate);
		}
		isLoading.set(false);

		// clear token refresh interval on component unmount
		return () => {
			intervalId && clearInterval(intervalId);
		};
	});

	// Provide a redirect page if you need.
	// It must be whitelisted in Auth0. I think.
	const login = async () => {
		await auth0.loginWithRedirect({
			redirect_uri: window.location.origin,
			prompt: 'login'
		});
	};

	const logout = () => {
		auth0.logout({
			returnTo: window.location.origin
		});
		isAuthenticated.set(false);
		userInfo.set({});
		authToken.set('');
		isLoading.set(true);
	};

	const auth = {
		login,
		logout
	};

	return auth;
}
