import { useEffect, useState } from "react"
import CheckIn from "~check-in"
import GroupManager from "~group-manager"
import GroupView from "~group-view"
import Join from "~join"
import Landing from "~landing"

function IndexPopup() {
  const [activeGroup, setActiveGroup] = useState(0)

  // Initialize with empty array instead of dummy data
  const [group, setGroup] = useState([])
  const [userEmotion, setUserEmotion] = useState("")
  const [view, setView] = useState(3)
  const [openPicker, setOpen] = useState(false)
  
  const get_emoji = async () => {
    const link = "http://140.232.178.49:8080/get_emotion"
    const token = localStorage.getItem("token")
    const response = await fetch(link, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({ 'token': token })
    })
    const jsonData = await response.json()
    if (jsonData.success){
      const emoji = jsonData['emotion']
      setUserEmotion(emoji)
      console.log(emoji)
    }
  }

  const updateGroup = async () => {
    try {
      const groups = await get_posts()
      if (groups && Array.isArray(groups)) {
        setGroup(groups)
      } else {
        console.error("Invalid group data format:", groups)
      }
    } catch (error) {
      console.error("Error updating groups:", error)
    }
  }

  useEffect(() => {
    get_emoji() 
  }, [])
  
  useEffect(() => {
    updateGroup()
    console.log("group updated")
    const interval = setInterval(updateGroup, 3000)
    return () => clearInterval(interval);
  }, []); 

  const get_posts = async () => {
    const link = "http://140.232.178.49:8080/load_groups"
    const token = localStorage.getItem("token")
    const response = await fetch(link, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({ login_token: token })
    })
    const jsonData = await response.json()
    console.log("Group data received:", jsonData.groups)
    return jsonData.groups
  }
  
  const check_jwt = async () => {
    const token = localStorage.getItem("token")
    const link = "http://140.232.178.49:8080/check_token"

    if (!token) {
      setView(3) 
      return
    }
    
    try {
      const response = await fetch(link, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        }
      })

      const jsonData = await response.json()
      console.log("Token verification response:", jsonData)

      if (jsonData.success === true) {
        if (jsonData.token && jsonData.token !== token) {
          localStorage.setItem("token", jsonData.token)
        }
        await updateGroup()
        setView(0) 
      } else {
        localStorage.removeItem("token")
        setView(3)
      }
    } catch (err) {
      console.error("Error during token verification:", err)
      setView(3) 
    }
  }
  
  useEffect(() => {
    console.log("Checking JWT and initializing app")
    check_jwt()
  }, [])

  // useEffect(() => {
  //   chrome.runtime.onMessage.addListener((message) => {
  //     if (message.triggeredBy === "alarm") {
  //       setView(1);
  //     }
  //   });
  // }, []);
  return (
    <div className="pop-up">
      {view == 0 && (
        <GroupView
          group={group}
          activeGroup={activeGroup}
          setActiveGroup={setActiveGroup}
          setView={setView}
          updateGroup={updateGroup}
        />
      )}
      {view == 1 && (
        <CheckIn
          currentEmotion={userEmotion}
          setCurrentEmotion={(emotion) => {
            setUserEmotion(emotion)
          }}
          setView={setView}
        />
      )}
      {view === 2 && <GroupManager groupList={group} setGroupList={setGroup} setView={() =>{setView(0)}}/>}
      {view === 3 && <Landing setView={setView} />}
    </div>
  )
}

export default IndexPopup