import { useState } from "react"

import "./styles.css"

export default function GroupForm({ setInCreator,setView }) {
  const [inputValue, setInputValue] = useState("")
  const [passwordValue, setPasswordValue] = useState("")

  const handleSubmit = (e) => {
    e.preventDefault()
    
    setInputValue("")
    setPasswordValue("")
    if(join_group()){
      alert(`Group Joined: ${inputValue}`)
      handleViewGroups()
      setInCreator(false)
      
    }
  }

  const handleViewGroups = () => {
    setView(0);  // Set the view to 0 (or any value corresponding to "View Groups")
  };

  const handleCreateGroup = () => {
    console.log("clicked")
    setInCreator(true)
    
    
  }
  const join_group = async () => {
    try{
      console.log("JJOOOOIN")
      const link = "http://140.232.178.49:8080/join_group"
      const token = localStorage.getItem("token")
      const response = await fetch(link, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },

        body: JSON.stringify({ 
          'group_name':inputValue,
          'passcode':passwordValue,
          
      
      })
      })
      const jsonData = await response.json()
      if (jsonData.success){
        return true
      }
      return false
      
    }catch(err){
      console.log(err)
    }
}
  return (
    <div>
      <div className="form-container">
        <div className="form-header">
          <p>Join a Group</p>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <input
              type="text"
              placeholder="Enter Group Name"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
            />
          </div>
          <div className="input-group">
            <input
              type="password"
              placeholder="Enter Group Password"
              value={passwordValue}
              onChange={(e) => setPasswordValue(e.target.value)}
            />
          </div>
          <div className="submit-join">
            <button type="submit">Submit</button>
          </div>
        </form>
      </div>
      <footer>
        <div className="create-group-button">
          <button
            type="button"
            onClick={handleCreateGroup}>
            Create New Group
          </button>
        </div>
      </footer>

      <div className="f-view-groups-button-container">
        <button type="button" className="f-view-groups-button" onClick={handleViewGroups}>
          View Groups
        </button>
      </div>
    </div>
  )
}