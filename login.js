let auth0 = null;

const fetchAuthConfig = () => fetch("auth_config.json");

const configureClient = async () => {
    const response = await fetchAuthConfig();
    const config = await response.json();

    auth0 = await createAuth0Client({
        domain: config.domain,
        client_id: config.clientId
    });
};

window.onload = async () => {
    await configureClient();

    // NEW - update the UI state
    updateUI();

    const isAuthenticated = await auth0.isAuthenticated();

    if(isAuthenticated){

        return;
    }

    // * NEW - check for the code and state parameters
    const query = window.location.search;
    if(query.includes("code=") && query.includes("state=")) {

        // * preocess the login state
        await auth0.handleRedirectCallback();

        updateUI();

        // * use replaceState to redirect the user away and remove the querystring parameter
        window.history.replaceState({}, document.title, "/");
        
    }
};

// NEW
const updateUI = async () => {

    const isAuthenticated = await auth0.isAuthenticated();

    document.getElementById("btn-logout").disabled = !isAuthenticated;
    document.getElementById("btn-login").disabled = isAuthenticated;

  // NEW - add logic to show/hide JISI meeting api
    if (isAuthenticated) {
        
        // * initialize the meeting API
        const domain = 'meet.jit.si';
        const options = {
            roomName: "Noorsmeeting/TestingThisMeeting",
            width: 700,
            height: 700,
            parentNode: document.querySelector('#meet'),
            configOverwrite: {
                startWithAudioMuted: false,
                startWithVideoMuted: true,
                requireDisplayName: true,
            },
            interfaceConfigOverwrite:
                {
                    SHOW_CHROME_EXTENSION_BANNER: false,
                }
        };
    const api = new JitsiMeetExternalAPI(domain, options);

    } else {
    document.getElementById("gated-content").classList.add("hidden");
    }
};

const login = async () => {
    await auth0.loginWithRedirect({
        redirect_uri: window.location.origin
    });
};

const logout = () => {
    auth0.logout({
        returnTo: window.location.origin
    });
};