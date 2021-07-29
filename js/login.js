// The Auth0 client, initialized in configureClient()
let auth0 = null;

// * Starts the authentication flow

const login = async (targetUrl) => {
    try {
        console.log("Logging in", targetUrl);

        const options = {
        redirect_uri: window.location.origin
        };

        if (targetUrl) {
        options.appState = { targetUrl };
        }

        await auth0.loginWithRedirect(options);
    } catch (err) {
        console.log("Log in failed", err);
    }
};


// * Executes the logout flow

const logout = () => {
    try {
        console.log("Logging out");
        auth0.logout({
        returnTo: window.location.origin
        });
    } catch (err) {
        console.log("Log out failed", err);
    }
};


// * Retrieves the auth configuration from the server

const fetchAuthConfig = () => fetch("/auth_config.json");


// * Initializes the Auth0 client

const configureClient = async () => {
    const response = await fetchAuthConfig();
    const config = await response.json();

    auth0 = await createAuth0Client({
        domain: config.domain,
        client_id: config.clientId,
        audience: config.audience
    });
};

/**
 * Checks to see if the user is authenticated. If so, `fn` is executed. Otherwise, the user
 * is prompted to log in
 * @param {*} fn The function to execute if the user is logged in
 */
const requireAuth = async (fn, targetUrl) => {
    const isAuthenticated = await auth0.isAuthenticated();

    if (isAuthenticated) {
        return fn();
    }

    return login(targetUrl);
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


const toggelUI = (isAuthenticated) => {
    
    // * Show & hide logout / login
    
    login_request = document.getElementById("login-request");
    login_btn = document.getElementById("btn-login");
    logout_btn = document.getElementById("btn-logout");
    call_api_btn = document.getElementById("btn-call-api");

    if(isAuthenticated){
        login_btn.style.display = "none";
        logout_btn.style.display = "block";
        call_api_btn.style.display = "block";
        login_request.style.display = "none";
        
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

        document.getElementById("btn-logout").style.display = "none";
        document.getElementById("btn-login").style.display = "block";
        login_request.style.display = "block";
        call_api_btn.style.display = "none";
    }    

};    



const callApi = async () => {
    try {

        // Get the access token from the Auth0 client
        const token = await auth0.getTokenSilently();
        let data = {
                    participants: ["Noor", "Ahmed"],
                    labels: ["WebRTC", "Authentication"]
                };    
        // Make the call to the API, setting the token        
        // in the Authorization header
        const response = await fetch("https://meetingtriggerapp.azurewebsites.net/api/insert?", {
            method: "POST",
            headers: {
                "Content-type": "application/json;charset=UTF-8",
                "Authorization": `Bearer ${token}`,
            },    
            body: JSON.stringify({
                participants: ['Noor', 'Ahmed'],
                labels: ['WebRTC', 'Authentication'],
            }),    
        });    

    } catch (e) {
        // Display errors in the console
        console.error(e);
    }    
};    
