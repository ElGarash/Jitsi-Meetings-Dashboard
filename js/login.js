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


const updateUI = async () => {

    const isAuthenticated = await auth0.isAuthenticated();
    
    toggelUI(isAuthenticated);
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


const toggelUI = (isAuthenticated) => {
    
    // * toggle logout / login
    login_request = document.getElementById("login-request");
    login_btn = document.getElementById("btn-login");
    logout_btn = document.getElementById("btn-logout");
    
    if(isAuthenticated){
        
        login_request.style.display = "none";
        logout_btn.style.display = "block";
        login_btn.style.display = "none";
        
        // * initialize the meeting API
        const domain = 'meet.jit.si';
        const options = {
            roomName: "Noorsmeeting/TestingThisMeeting",
            
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

        login_request.style.display = "block";
        document.getElementById("btn-logout").style.display = "none";
        document.getElementById("btn-login").style.display = "block";
    }

};