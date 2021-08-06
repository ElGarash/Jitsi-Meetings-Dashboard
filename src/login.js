// The Auth0 client, initialized in configureClient()
let auth0 = null;

// * Starts the authentication flow
// TODO: change the @App_REDIRECT_URI to work on the website
const APP_REDIRECT_URI = window.location.origin;
const login = async (targetUrl) => {
    try {
        console.log("Logging in", targetUrl);

        const options = {
            redirect_uri: APP_REDIRECT_URI,
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
            returnTo: APP_REDIRECT_URI,
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
        audience: config.audience,
        redirect_uri: APP_REDIRECT_URI
    });
};

/**
 * Checks to see if the user is authenticated. If so, `fn` is executed. Otherwise, the user
 * is prompted to log in
 * @param {*} fn The function to execute if the user is logged in
 */
const requireAuth = async (fn, targetUrl) => {
    const isAuthenticated = await auth0.isAuthenticated();

    return login(targetUrl);
};

window.onload = async () => {
    await configureClient();
    

    // NEW - update the UI state
    updateUI();
    
    // * NEW - check for the code and state parameters
    const query = window.location.search;
    if (query.includes("code=") && query.includes("state=")) {
        // * process the login state
        await auth0.handleRedirectCallback();
        
        updateUI();
        
        // * use replaceState to redirect the user away and remove the querystring parameter
        // TODO change the the origin from "/" to "/meetings"
        window.history.replaceState({}, document.title, "/");
    }
};

const updateUI = async () => {
    const isAuthenticated = await auth0.isAuthenticated();
    
    // * Show & hide logout / login
    
    window.hello_message = document.getElementById("hello-message");
    window.login_btn = document.getElementById("login");
    window.logout_btn = document.getElementById("logout");
    window.send_participants_btn = document.getElementById("send-participants");
    window.room_list = document.getElementById("room-list");
    window.start_streaming_btn = document.getElementById("start-streaming");
    window.end_streaming_btn = document.getElementById("end-streaming");
    window.dashboard_btn = document.getElementById("dashboard");
    window.close_meeting_btn = document.getElementById("close-meeting");
    window.rooms = document.getElementById("rooms");
    
    if (isAuthenticated) {
        login_btn.classList.add("hide");
        hello_message.classList.add("hide");
        logout_btn.classList.remove("hide");
        room_list.classList.remove("hide");
        
        getActiveRooms();

    } else {
        hello_message.classList.remove("hide");
        login_btn.classList.remove("hide");
        logout_btn.classList.add("hide");
        send_participants_btn.classList.add("hide");
        room_list.classList.add("hide");
        dashboard_btn.classList.add("hide");
        start_streaming_btn.classList.add("hide");
        end_streaming_btn.classList.add("hide");
        close_meeting_btn.classList.add("hide");

    }

};


const createMeeting = async () => {

    // * prevent default behavior of form
    document.getElementById("create-room").onsubmit = event => event.preventDefault();

    const meeting_labels = document.getElementById("roomLabels").value;
    const room_name = roomName();
    console.log("room name:", room_name)

    if(!meeting_labels){
        console.log("file the text fields");
        return;
    }

    const url = "https://meetingtriggerapp.azurewebsites.net/dashboard/meetings";
    // * send request to database to store meeting
    const response = await sendRequest(url, "POST", {
        roomName: room_name,
        labels: meeting_labels.split(',')
    });

    if(!response.ok){
        alert("Error occurred please tray later")
        return;
    }
    // * call Jitsi api
    await callJitsiAPI(room_name.replaceAll(' ', '_'));
    api.executeCommand('subject', meeting_labels);
    
    const response_data = await response.json();

    window.room_id = response_data.id;
    console.log("room_id from createMeeting:", room_id);

    

    room_list.classList.add("hide");
    start_streaming_btn.classList.remove("hide");
    close_meeting_btn.classList.remove("hide");
    send_participants_btn.classList.remove("hide");


    console.log(`API response for start meeting: ${response_data}`);
};

const sendParticipants = async () => {

    // * get participants names and labels of the meeting
    const participants_names = api.getParticipantsInfo().map((p) => p.displayName);

    if(!participants_names.length){
        alert("initialize meeting first");
        return;
    }

    const url = `https://meetingtriggerapp.azurewebsites.net/dashboard/meetings/${window.room_id}`;
    const response =  await sendRequest(url, "PATCH", 
    {participants: participants_names});

    if(!response.ok){
        alert("Server is unreachable right now pleas try again");
    }
    console.log("send Participants response", response.ok);

};


const getActiveRooms = async () => {
    const url = "https://meetingtriggerapp.azurewebsites.net/dashboard/meetings"
    
    let response = await sendRequest(url, "GET", null);
    while(!response.ok){
        response = await sendRequest(url, "GET", null);
        console.log("you had successfully fetched the data with response:", response.ok)
    };
    
    const response_data = await response.json();
    console.log("response from getActiveRooms", response_data["activeMeetings"])
    
    if(!response.ok){
        alert("Server is unreachable right now pleas try agin");
        return
    }

    response_data["activeMeetings"].map(room => {
        const h2 = document.createElement("h2")
        h2.classList.add("room-name")
        h2.textContent = room.labels.join(", ");
        h2.addEventListener("click", async () => {
            await callJitsiAPI(room.name);
            api.executeCommand('subject', room.labels.join(", "));
            window.room_id = room.id;
            console.log("room_id from getActiveRooms:", room_id);
            
            room_list.classList.add("hide");
            start_streaming_btn.classList.remove("hide");
            close_meeting_btn.classList.remove("hide");
            send_participants_btn.classList.remove("hide");
        })
        
        rooms.appendChild(h2);
    })
    
};

const closeRoom = () => {
    if(typeof api === "undefined"){
        alert("this feature works only if you are in a room");
        return
    }
    delete window.api;
    
    getActiveRooms();

    document.getElementById("room").innerHTML = '';
    rooms.innerHTML = '';
    room_list.classList.remove("hide");
    start_streaming_btn.classList.add("hide");
    send_participants_btn.classList.add("hide");
    close_meeting_btn.classList.add("hide");
    end_streaming_btn.classList.add("hide");
    document.getElementById("room").classList.add("hide");

};


// * start video stream of the running meeting on YouTube
const startStream = () => {
    
    // * check if their is a running meeting
    if(!api.getNumberOfParticipants()){
        console.log("You can not start streaming without starting a meeting.")
        return
    }
    
    api.executeCommand('startRecording', {
        mode: `stream`, //recording mode, either `file` or `stream`.
        shouldShare: true, //whether the recording should be shared with the participants or not. Only applies to certain jitsi meet deploys.
        youtubeStreamKey: `8fx0-x8a3-jyr6-sp69-dmqw`, //the YouTube stream key.
        youtubeBroadcastID: `` //the YouTube broadcast ID.
    });

    start_streaming_btn.classList.add("hide");
    end_streaming_btn.classList.remove("hide");
};

const endStream = () => {
    api.executeCommand('stopRecording', mode='stream');
    
    end_streaming_btn.classList.add("hide");
    start_streaming_btn.classList.remove("hide");
};





// * send request to Database API
// * return a json object of the response
const sendRequest = async (url, method, body) => {
    try {
        
        // Get the access token from the Auth0 client
        const token = await auth0.getTokenSilently();
        // Make the call to the API, setting the token
        // in the Authorization header
        const response = await fetch(url, {
            method: method,
            headers: {
                "Content-type": "application/json;charset=UTF-8",
                "Authorization": `Bearer ${token}`,
                "Access-Control-Allow-Origin": "*"
            },
            body: body ? JSON.stringify(body) : undefined,
        });

        return response;
    } catch (e) {
        // Display errors in the console
        console.error(e);
        console.log("Some thing goes wrong with the request makes it fails.", e);
    }
}

const callJitsiAPI = async (room_name) => {

    try {
        // * get the name of user
        const user = await auth0.getUser();
        
        // * initialize the meeting API
        const domain = "meet.jit.si";
        const options = {
            roomName: room_name,
            
            parentNode: document.querySelector("#room"),
            userInfo: {
                displayName: user["name"],
            },
            configOverwrite: {
                startWithAudioMuted: false,
                startWithVideoMuted: true,
                requireDisplayName: true,

                NATIVE_APP_NAME: 'ELgarash',
                SHOW_JITSI_WATERMARK: true,
                // DEFAULT_BACKGROUND: '#474747',
                // DEFAULT_LOGO_URL: 'images/watermark.svg',
                // DEFAULT_WELCOME_PAGE_LOGO_URL: 'images/watermark.svg',
            },
            interfaceConfigOverwrite: {
                SHOW_CHROME_EXTENSION_BANNER: false,
            },
        };
        
        window.api = new JitsiMeetExternalAPI(domain, options);

        window.participants = new Set(api.getParticipantsInfo().map((p) => p.participantId));
        
        document.getElementById("room").classList.remove("hide");
        // * handle room close when meeting is finished
        autoClose();
        
    }catch(e) {
        console.log("Error when calling Jitsi api", e);
    }
    
};

const autoClose = () => {

    api.addEventListener("participantJoined", (participant) => {
        participants.add(participant.id);
    });

    api.addEventListener("participantLeft", async (_) => {
        if(participants.size > 0 && api.getNumberOfParticipants() === 1){

            const url = `https://meetingtriggerapp.azurewebsites.net/dashboard/meetings/${window.room_id}`;
            const response = sendRequest(url, "PATCH", 
            {endingFlag: true});
            
            // console.log("send Participants response", response);
        }
    });
};


const roomName = () => {
    // Declare all characters
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

    // Pick characters randomly
    let room_name = '';
    for (let i = 0; i < 30; i++) {
        room_name += chars.charAt(Math.floor(Math.random() * chars.length));
    }

    return room_name;

};
