import { useState } from "react"

export default function GroupCreator({ setInCreator,setView }) {
  const [groupName, setGroupName] = useState("")
  const [password, setPassword] = useState("")
  const [isAnonymous, setIsAnonymous] = useState(false)
  const [checkinInterval, setCheckinInterval] = useState("")

  const handleSubmit = (e) => {
    e.preventDefault()
    if (create_group()){
      alert(`Group Created: ${groupName}`)
      setView(0)
      console.log("Group Created")
      setInCreator(false)
    }
    
    // 
  }
  const create_group = async () => {
    try{
      const link = "http://140.232.178.49:8080/create_group"
      const token = localStorage.getItem("token")
      const response = await fetch(link, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },

        body: JSON.stringify({ 
          'group_name':groupName,
          'is_anonymous':isAnonymous,
          'passcode':password,
          'interval': checkinInterval
      
      })
      })
      const jsonData = await response.json()
      return true
    }catch(err){
      console.log(err)
    }
}
  return (
    <form onSubmit={handleSubmit} className="c-form">
      <div className="c-groupname">
        <label htmlFor="group-name">Group Name:</label>
        <input
          id="group-name"
          type="text"
          placeholder="Enter group name"
          value={groupName}
          onChange={(e) => setGroupName(e.target.value)}
        />
      </div>

      <div className="c-password">
        <label htmlFor="password">Password:</label>
        <input
          id="password"
          type="password"
          placeholder="Enter password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>

      <div className="c-anonymous">
        <label>Anonymous?</label>
        <label>
          <input
            type="checkbox"
            name="anonymous"
            value="yes"
            checked={isAnonymous}
            onChange={() => setIsAnonymous((prev) => !prev)}
          />
        </label>
      </div>

      <div className="c-interval">
        <label htmlFor="checkin-interval">
          Check-in Interval (in minutes):
        </label>
        <input
          id="checkin-interval"
          type="number"
          placeholder="Enter interval in minutes"
          value={checkinInterval}
          onChange={(e) => setCheckinInterval(e.target.value)}
        />
      </div>

      <div className="c-submit">
        <button type="submit">Submit</button>
      </div>
    </form>
  )
}