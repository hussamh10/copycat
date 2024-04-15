const WebSocket = require('ws');
const { Innertube, UniversalCache } = require('youtubei.js');
// get user name and port from command line arguments
const user_port = process.argv[2];
console.log(`User port: ${user_port}`);
const wss = new WebSocket.Server({ port: user_port });

let yt = null; // Global YouTube client instance

async function addToWatchHistory(yt, videoId) {
    let videoInfo = await yt.getInfo(videoId);
    await videoInfo.addToWatchHistory();
}

async function getInfo(yt, videoId) {
    let videoInfo = await yt.getInfo(videoId);
    return videoInfo;
}

async function getHomepage(yt) {
  const homepageFeed = await yt.getHomeFeed();
  console.log('Home Page:', homepageFeed.videos);
  const videos = homepageFeed.videos;
  return videos;
}

async function getTranscript(yt, videoId) {

    const videoInfo = await yt.getInfo(videoId);
    try {
        const transcriptInfo = await videoInfo.getTranscript();
        const transcriptLines = transcriptInfo.transcript.content.body.initial_segments.map(segment => segment.snippet.text);
        return transcriptLines;
    } catch (error) {
        console.log('Transcript not available for this video');
        return [];
    }
}

async function getUpNextRecommendations(yt, videoId) {
    videoInfo = await yt.getInfo(videoId);
    watchNext = await videoInfo.watch_next_feed;
    const filteredContents = watchNext.filter(item => item.type === 'CompactVideo');
    filteredContents.forEach((video, index) => {
        console.log(`Suggested Video ${index + 1}: ${video.title.text} (ID: ${video.id})`);
    });
    // const titles = filteredContents.map(video => video.title.text);
    const ids = filteredContents.map(video => video.id);
    return ids;
}

async function signinBlank() {
    console.log('Signing in with blank credentials...');
    yt = await Innertube.create({});
  }

async function signin(username) {
  file = `./creds/${username}`;
  console.log(`Using credentials file: ${file}`);
  try {
    yt = await Innertube.create({
      cache: new UniversalCache(true, file)
    });

    yt.session.on('auth-pending', (data) => {
      console.log(`Go to ${data.verification_url} in your browser and enter code ${data.user_code} to authenticate.`);
    });

    yt.session.on('auth', ({ credentials }) => {
      console.log('Sign in successful:', credentials);
    });

    yt.session.on('update-credentials', ({ credentials }) => {
      console.log('Credentials updated:', credentials);
    });

    await yt.session.signIn();
    await yt.session.oauth.cacheCredentials();

    return { status: "success", message: "Signed in successfully"};
  } catch (error) {
    console.error("Sign-in error:", error);
    return { status: "error", message: error.message };
  }
}

async function callFunctionByName(functionName, args) {
  switch (functionName) {
    case "signinBlank":
      await signinBlank();
      return { status: "success", message: "Signed in successfully"};
    case "signin":
      const signInResult = await signin(...args);
      return signInResult;
    case "addToWatchHistory":
      return await addToWatchHistory(yt, ...args);
    case "getUpNextRecommendations":
      return await getUpNextRecommendations(yt, ...args);
    case "getInfo":
      return await getInfo(yt, ...args);
    case "getTranscript":
      return await getTranscript(yt, ...args);
    case "getHomePage":
      return await getHomepage(yt);
    default:
      console.log(`Function ${functionName} not found.`);
      throw new Error(`Function ${functionName} not found.`);
  }
}

wss.on('connection', function connection(ws) {
  ws.on('message', async function incoming(message) {
    try {
      const { functionName, args } = JSON.parse(message);
      const result = await callFunctionByName(functionName, args);
      ws.send(JSON.stringify({ status: "success", result: result }));
    } catch (error) {
      ws.send(JSON.stringify({ status: "error", message: error.message }));
    }
  });
});

console.log('WebSocket server started on port ' + user_port);