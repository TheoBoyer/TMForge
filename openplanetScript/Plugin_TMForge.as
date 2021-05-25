#name "TMForge"
#author "Théo Boyer"
#category "Reinforcement learning"


bool inGame = false;
bool strictMode = false;
string curMap = "";
string game_state = "";

uint preCPIdx = 0;
uint curCP = 0;
uint maxCP = 0;
int currTime = 0;
auto sock = Net::Socket();

void SendMessage(const string message) {
  if(sock.CanWrite()) {
      if(!sock.WriteRaw(message)) {
        sock.Close();
        if(!sock.Connect("localhost", 50000)) {
            print("Server isn't turned on");
            sock.Close();
        }
      } else {
        //print("Sent data");
      }
  } else {
    //print("Not yet connected");
  }
}

string EUISequenceToString(EUISequence seq) {
  string resp = "";
  if(seq == EUISequence::None) {
    resp = "None";
  } else if(seq == EUISequence::Playing) {
    resp = "Playing";
  } else if(seq == EUISequence::Intro) {
    resp = "Intro";
  } else if(seq == EUISequence::Outro) {
    resp = "Outro";
  } else if(seq == EUISequence::Podium) {
    resp = "Podium";
  } else if(seq == EUISequence::CustomMTClip) {
    resp = "CustomMTClip";
  } else if(seq == EUISequence::EndRound) {
    resp = "EndRound";
  } else if(seq == EUISequence::PlayersPresentation) {
    resp = "PlayersPresentation";
  } else if(seq == EUISequence::UIInteraction) {
    resp = "UIInteraction";
  } else if(seq == EUISequence::RollingBackgroundIntro) {
    resp = "RollingBackgroundIntro";
  } else if(seq == EUISequence::CustomMTClip_WithUIInteraction) {
    resp = "CustomMTClip_WithUIInteraction";
  } else if(seq == EUISequence::Finish) {
    resp = "Finish";
  }
  return resp;
}

void Update(float dt) {
  CGamePlaygroundUIConfig@ uiconfig = GetApp().CurrentPlayground.UIConfigs[0];
  game_state = EUISequenceToString(uiconfig.UISequence);
  string inGameStr = "false";
  if(inGame) {
    inGameStr = "true";
  }
  SendMessage('{"t": ' + Time::get_Stamp() + ', "in_game": ' + inGameStr + ', "game_state": "' + game_state + '", "time": ' + currTime + ', "CP": ' + curCP + ', "maxCP": ' + maxCP + "}");
  
  if(cast<CSmArenaClient>(GetApp().CurrentPlayground) !is null) {
    CSmArenaClient@ playground = cast<CSmArenaClient>(GetApp().CurrentPlayground);
    if(playground.GameTerminals.Length <= 0
       || playground.GameTerminals[0].UISequence_Current != ESGamePlaygroundUIConfig__EUISequence::Playing
       || cast<CSmPlayer>(playground.GameTerminals[0].GUIPlayer) is null
       || playground.Arena is null
       || playground.Map is null) {
      inGame = false;
      return;
    }
    CSmPlayer@ player = cast<CSmPlayer>(playground.GameTerminals[0].GUIPlayer);
    MwFastBuffer<CGameScriptMapLandmark@> landmarks = playground.Arena.MapLandmarks;
    
    if(!inGame && (curMap != playground.Map.IdName || GetApp().Editor !is null)) {
      // keep the previously-determined CP data, unless in the map editor
      curMap = playground.Map.IdName;
      preCPIdx = player.CurrentLaunchedRespawnLandmarkIndex;
      curCP = 0;
      maxCP = 0;
      strictMode = true;
      
      array<int> links = {};
      for(uint i = 0; i < landmarks.Length; i++) {
        if(landmarks[i].Waypoint !is null && !landmarks[i].Waypoint.IsFinish && !landmarks[i].Waypoint.IsMultiLap) {
          // we have a CP, but we don't know if it is Linked or not
          if(landmarks[i].Tag == "Checkpoint") {
            maxCP++;
          } else if(landmarks[i].Tag == "LinkedCheckpoint") {
            if(links.Find(landmarks[i].Order) < 0) {
              maxCP++;
              links.InsertLast(landmarks[i].Order);
            }
          } else {
            // this waypoint looks like a CP, acts like a CP, but is not called a CP.
            if(strictMode) {
              warn("The current map, " + string(playground.Map.MapName) + " (" + playground.Map.IdName + "), is not compliant with checkpoint naming rules."
                   + " If the CP count for this map is inaccrate, please report this map to Phlarx#1765 on Discord.");
            }
            maxCP++;
            strictMode = false;
          }
        }
      }
    }
    inGame = true;
    
    if(preCPIdx != player.CurrentLaunchedRespawnLandmarkIndex) {
      preCPIdx = player.CurrentLaunchedRespawnLandmarkIndex;
      if(landmarks[preCPIdx].Waypoint is null || landmarks[preCPIdx].Waypoint.IsFinish || landmarks[preCPIdx].Waypoint.IsMultiLap) {
        // if null, it's a start block. if the other flags, it's either a multilap or a finish.
        // in both cases, we reset the completed cp count to zero.
        curCP = 0;
      } else {
        curCP++;
      }
    }
    currTime = player.ScriptAPI.CurrentRaceTime;
  } else {
    inGame = false;
  }
}

void Main() {
    if(!sock.Connect("localhost", 50000)) {
        print("Server isn't turned on");
        return;
    }
    print("Connecting...");
}