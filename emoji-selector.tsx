import data from "@emoji-mart/data"
import Picker from "@emoji-mart/react"
import { useEffect } from "react"

export default function EPick({ setOpen, setCurrentEmotion }) {
  const emojiSelect = (emotion) => {
    set_emoji(emotion)
    setCurrentEmotion(emotion)
    setOpen(false)
  }
  const set_emoji = async (emoji) => {
    
      const link = "http://140.232.178.49:8080/change_emoji"
      const token = localStorage.getItem("token")
      const response = await fetch(link, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ 'new_emoji':emoji.native})
      })
      const jsonData = await response.json()
      console.log("SETEMOJI")
      console.log(jsonData)
  }


  return (
    <>
      <div onClick={() => setOpen(false)} className="emoji-selector-close">Close</div>
      <div className="actual-emoji-selector">
        <Picker categories={["people"]} data={data} onEmojiSelect={emojiSelect} />
      </div>
    </>
  )
}